from terno.models import DataSource, Table, TableColumn
from django.dispatch import receiver
from django.db.models.signals import post_save
import sqlalchemy
import terno.utils as utils
import sqlshield
from sqlshield.models import MDatabase

# TODO: delete the extra tables and columns
def load_metadata(datasource):
    engine = utils.create_db_engine(datasource.type, datasource.connection_str,
                                    credentials_info=datasource.connection_json)
    if not datasource.dialect_name or not datasource.dialect_version:
        with engine.connect():
            datasource.dialect_name = engine.dialect.name
            datasource.dialect_version = str(engine.dialect.server_version_info)
            datasource.save(update_fields=['dialect_name', 'dialect_version'])

    inspector = sqlalchemy.inspect(engine)

    mdb = MDatabase.from_inspector(inspector)
    
    for tbl_name, tbl in mdb.tables.items():
        existing_tables = Table.objects.filter(
            name=tbl_name, data_source=datasource)
        if existing_tables:
            mtable = existing_tables.first()
        else:
            mtable = Table.objects.create(
                name=tbl_name, public_name=tbl_name,
                data_source=datasource)
        current_tabcols = []
        #current_tables[tbl_name] = current_tabcols
        for col_name, col in tbl.columns.items():
            print(tbl_name, col_name)
            print("col: ", col)
            print("\tTYPE: ", col.type)
            print("----")
            dbcol = TableColumn.objects.filter(
                name=col_name, table=mtable)
            if not dbcol:
                TableColumn.objects.create(
                    name=col_name, public_name=col_name,
                    table=mtable, data_type=str(col.type))
            current_tabcols.append(col)
    print("Finished building the tables!!")
    # return current_tables


@receiver(post_save, sender=DataSource)
def update_tables_on_datasource_change(sender, instance, created, **kwargs):
    """Fetches and saves table information when a data source is saved."""
    load_metadata(instance)
    # if created:
    #     for table_name in retrieved_tables:
    #         Table.objects.create(name=table_name, data_source=instance)
