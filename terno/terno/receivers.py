from terno.models import DataSource, Table, TableColumn
from django.dispatch import receiver
from django.db.models.signals import post_save
import sqlalchemy


# TODO: delete the extra tables and columns
def load_metadata(datasource):
    engine = sqlalchemy.create_engine(datasource.connection_str)
    if not datasource.db_info:
        with engine.connect():
            dialect_name = engine.dialect.name
            version_info = engine.dialect.server_version_info
            datasource.db_info = dialect_name + ' version ' + str(version_info)
            datasource.save(update_fields=['db_info'])

    inspector = sqlalchemy.inspect(engine)
    schemas = inspector.get_schema_names()
    current_tables = {}
    for schema in schemas[:1]:
        for table_name in inspector.get_table_names(schema=schema):
            existing_tables = Table.objects.filter(
                name=table_name, data_source=datasource)
            if existing_tables:
                mtable = existing_tables.first()
            else:
                mtable = Table.objects.create(
                    name=table_name, public_name=table_name,
                    data_source=datasource)
            current_tabcols = []
            current_tables[table_name] = current_tabcols
            for col in inspector.get_columns(table_name, schema=schema):
                dbcol = TableColumn.objects.filter(
                    name=col['name'], table=mtable)
                if not dbcol:
                    TableColumn.objects.create(
                        name=col['name'], public_name=col['name'],
                        table=mtable, data_type=col['type'])
                current_tabcols.append(col)
    return current_tables


@receiver(post_save, sender=DataSource)
def update_tables_on_datasource_change(sender, instance, created, **kwargs):
    """Fetches and saves table information when a data source is saved."""
    load_metadata(instance)
    # if created:
    #     for table_name in retrieved_tables:
    #         Table.objects.create(name=table_name, data_source=instance)
