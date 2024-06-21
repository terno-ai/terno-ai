import terno.models as models
from django.views.decorators.cache import cache_page


def get_all_group_tables(datasource, roles):
    table_object = models.TableSelector.objects.filter(
        data_source=datasource).first()
    global_tables = table_object.tables.all()
    group_tables_object = models.GroupTableSelector.objects.filter(
        group__in=roles,
        tables__data_source=datasource).first()  # Take tables for all groups
    group_tables = group_tables_object.tables.all()
    all_group_tables = global_tables.union(group_tables)
    print('global tables', global_tables)
    print('group tables', group_tables)
    print('final tables', all_group_tables)
    return all_group_tables


# @cache_page(24*3600)
def get_admin_config_object(datasource, roles):
    all_group_tables = get_all_group_tables(datasource, roles)
    all_group_tables_ids = list(all_group_tables.values_list('id', flat=True))
    table_columns = models.TableColumn.objects.filter(table_id__in=all_group_tables_ids)
    group_columns_object = models.GroupColumnSelector.objects.filter(
        group__in=roles,
        columns__in=table_columns).first()
    group_columns = group_columns_object.get_pub_column()
    print('final columns', group_columns)
    # response = f'Got {all_group_tables.count()} tables and {group_columns.count()} columns'
    return all_group_tables, group_columns
