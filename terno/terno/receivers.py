
from terno.models import DataSource, Table, TableColumn
from django.dispatch import receiver
from django.db.models.signals import post_save

import sqlalchemy
from sqlalchemy import inspect


# TODO: delete the extra tables and columns
def load_metadata(datasource):
    engine = sqlalchemy.create_engine(datasource.connection_str)
    inspector = inspect(engine)
    schemas = inspector.get_schema_names()
    current_tables = {}
    for schema in schemas[:1]:
        for table_name in inspector.get_table_names(schema=schema):
            existing_tables = Table.objects.filter(name=table_name, data_source=datasource)
            if len(existing_tables) > 0:
                mtable = existing_tables[0]
            else:
                mtable = Table(name=table_name, public_name=table_name, data_source=datasource)
                mtable.save()
            current_tabcols = []
            current_tables[table_name] = current_tabcols
            for col in inspector.get_columns(table_name, schema=schema):
                dbcol = TableColumn.objects.filter(name=col, table=mtable)
                if len(dbcol) > 0:
                    tabcol = dbcol[0]
                else:
                    tabcol = TableColumn(name=col['name'], table=mtable, data_type=col['type'])
                    tabcol.save()
                current_tabcols.append(col)
    return current_tables


@receiver(post_save, sender=DataSource)
def update_tables_on_datasource_change(sender, instance, created, **kwargs):
    """Fetches and saves table information when a data source is saved."""
    print("SIGNAL is fired!! I will load the models here.")
    load_metadata(instance)
    if created:
        print("Created: SIGNAL is fired!! I will load the models here.")
        # for table_name in retrieved_tables:
        #   Table.objects.create(name=table_name, data_source=instance)
