from terno.models import DataSource, Table, TableColumn, ForeignKey
from django.dispatch import receiver
from django.db.models.signals import post_save
import sqlalchemy
import terno.utils as utils
from sqlshield.models import MDatabase
import terno.models as models
from django.core.cache import cache


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
        for col_name, col in tbl.columns.items():
            dbcol = TableColumn.objects.filter(
                name=col_name, table=mtable)
            if not dbcol:
                TableColumn.objects.create(
                    name=col_name, public_name=col_name,
                    table=mtable, data_type=str(col.type))
            current_tabcols.append(col)

    for tbl_name, tbl in mdb.tables.items():
        foreign_keys = tbl.Foreign_Keys
        table = Table.objects.filter(
            name=tbl_name, data_source=datasource
        ).first()
        for fk in foreign_keys:
            constrained_columns = TableColumn.objects.filter(
                name=fk.constrained_columns[0].name,
                table__data_source=datasource).first()
            referred_table = Table.objects.filter(
                name=fk.referred_table.name, data_source=datasource).first()
            referred_columns = TableColumn.objects.filter(
                name=fk.referred_columns[0].name,
                table__data_source=datasource).first()
            dbfk = ForeignKey.objects.filter(
                constrained_table=table,
                constrained_columns=constrained_columns,
                referred_table=referred_table,
                referred_columns=referred_columns
            )
            if not dbfk:
                ForeignKey.objects.create(
                    constrained_table=table,
                    constrained_columns=constrained_columns,
                    referred_table=referred_table,
                    referred_columns=referred_columns
                )

    print("Finished building the tables!!")


@receiver(post_save, sender=DataSource)
def update_tables_on_datasource_change(sender, instance, created, **kwargs):
    """Fetches and saves table information when a data source is saved."""
    load_metadata(instance)
    # if created:
    #     for table_name in retrieved_tables:
    #         Table.objects.create(name=table_name, data_source=instance)


def delete_cache(datasource):
    org_data_source = models.OrganisationDataSource.objects.filter(
        datasource=datasource).first()
    org_users = models.OrganisationUser.objects.filter(organisation=org_data_source.organisation)
    for org_user in org_users:
        roles = org_user.user.groups.all()
        role_ids = sorted(roles.values_list('id', flat=True))
        cache_key = f"datasource_{datasource.id}_roles_{'_'.join(map(str, role_ids))}"
        cache.delete(cache_key)


@receiver(post_save, sender=models.TableRowFilter)
@receiver(post_save, sender=models.GroupTableRowFilter)
@receiver(post_save, sender=models.GroupColumnSelector)
@receiver(post_save, sender=models.PrivateColumnSelector)
@receiver(post_save, sender=models.GroupTableSelector)
@receiver(post_save, sender=models.PrivateTableSelector)
@receiver(post_save, sender=models.ForeignKey)
@receiver(post_save, sender=models.TableColumn)
@receiver(post_save, sender=models.Table)
def delete_cache_for_datasource(sender, instance, created, **kwargs):
    if sender is models.Table:
        data_source = instance.data_source
    if sender is models.TableColumn:
        data_source = instance.table.data_source
    if sender is models.ForeignKey:
        data_source = instance.constrained_table.data_source
    if sender is models.PrivateTableSelector:
        data_source = instance.data_source
    if sender is models.GroupTableSelector:
        # TODO
        # data_source = instance.data_source
        pass
    if sender is models.PrivateColumnSelector:
        data_source = instance.data_source
    if sender is models.GroupColumnSelector:
        # TODO
        # data_source = instance.data_source
        pass
    if sender is models.GroupTableRowFilter:
        data_source = instance.data_source
    if sender is models.TableRowFilter:
        data_source = instance.data_source

    if not created:
        delete_cache(data_source)
