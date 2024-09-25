from sqlshield.models import MDatabase
import terno.models as models
import terno.utils as utils
import sqlalchemy


class MDBPreparer:
    def __init__(self, datasource, roles):
        self.datasource = datasource
        self.roles = roles
        self.allowed_tables = None
        self.allowed_columns = None
        self.mdb = None

    def prepare(self):
        allowed_tables, allowed_colummns = self._get_admin_config_object()
        self._generate_mdb()
        self._keep_only_tables(allowed_tables)
        self._keep_only_columns(allowed_tables, allowed_colummns)
        tables = self.mdb.get_table_dict()
        self._update_table_descriptions(tables)
        self._update_filters(tables, self.datasource, self.roles)
        return self.mdb

    def _get_admin_config_object(self):
        all_group_tables = self.get_all_group_tables()
        group_columns = self.get_all_group_columns(all_group_tables)
        return all_group_tables, group_columns

    def _generate_mdb(self):
        engine = utils.create_db_engine(
            self.datasource.type,
            self.datasource.connection_str,
            credentials_info=self.datasource.connection_json)
        inspector = sqlalchemy.inspect(engine)
        self.mdb = MDatabase.from_inspector(inspector)

    def _keep_only_tables(self, allowed_tables):
        self.mdb.keep_only_tables(allowed_tables.values_list('name', flat=True))

    def _keep_only_columns(self, allowed_tables, allowed_colummns):
        '''
        As there is no keep_only_columns method on mDb
        we use the drop columns method on table
        '''
        for _, table in self.mdb.tables.items():
            table_obj = allowed_tables.filter(name=table.name)
            if table_obj:
                table.pub_name = table_obj.first().public_name
                keep_columns = allowed_colummns.filter(table__name=table.name).values_list('name', flat=True)
                table_columns = models.TableColumn.objects.filter(
                    table__in=table_obj).values_list('name', flat=True)
                drop_columns = set(table_columns).difference(keep_columns)
                table.drop_columns(drop_columns)
                for _, col in table.columns.items():
                    allowed_column = allowed_colummns.filter(table=table_obj.first(), name=col.name)
                    if allowed_column:
                        col.pub_name = allowed_column.first().public_name

    def _update_table_descriptions(self, tables):
        for tbl_name, tbl_object in tables.items():
            table_description = models.Table.objects.filter(
                public_name=tbl_name).first().description
            tbl_object.desc = table_description

    def _update_filters(self, tables):
        tbl_base_filters = self._get_base_filters(self.datasource) # table_name -> ["(a=2)", "(x = 1) or (y = 2)"]
        tbls_grp_filter = self._get_grp_filters(self.datasource, self.roles)
        self._merge_grp_filters(tbl_base_filters, tbls_grp_filter)
        for tbl, filters_list in tbl_base_filters.items():
            if len(filters_list) > 0:
                tables[tbl].filters = 'WHERE ' + ' AND '.join(filters_list)

    def _get_base_filters(self):
        tbl_base_filters = {}
        for trf in models.TableRowFilter.objects.filter(data_source=self.datasource):
            filter_str = trf.filter_str.strip()
            if len(filter_str) > 0:
                tbl_base_filters[trf.table.name] = ["(" + filter_str + ")"]
        return tbl_base_filters

    def _get_grp_filters(self):
        tbls_grp_filter = {}  # key: table_name, value = [filter1, filter2]
        for gtrf in models.GroupTableRowFilter.objects.filter(data_source=self.datasource, group__in=self.roles):
            filter_str = gtrf.filter_str.strip()
            if len(filter_str) > 0:
                tbl_name = gtrf.table.name
                lst = []
                if tbl_name not in tbls_grp_filter:
                    tbls_grp_filter[tbl_name] = lst
                else:
                    lst = tbls_grp_filter[tbl_name]
                lst.append("(" + filter_str + ")")
        return tbls_grp_filter

    def _merge_grp_filters(self, tbl_base_filters, tbls_grp_filter):
        '''
        Updates the row filter for each table in tables based on TableRowFIlter or GroupTableFilter.
        argument `tables' should be a dictionary of name and Mtable.

        '''
        for tbl, grp_filters in tbls_grp_filter.items():
            role_filter_str = " ( " + ' OR '.join(grp_filters) + " ) "
            all_filters = []
            if tbl in tbl_base_filters:
                all_filters = tbl_base_filters[tbl]
            else:
                tbl_base_filters[tbl] = all_filters
            all_filters.append(role_filter_str)

    def get_all_group_tables(self):
        # Get all tables from datasource
        global_tables = models.Table.objects.filter(
            data_source=self.datasource)
        # Get private tables in datasource
        private_table_object = models.PrivateTableSelector.objects.filter(
            data_source=self.datasource).first()
        if private_table_object:
            private_tables_ids = private_table_object.tables.all().values_list('id', flat=True)
            # Get tables excluding private tables
            global_tables = global_tables.exclude(id__in=private_tables_ids)

        # Add tables accessible by the user's groups
        group_tables_object = models.GroupTableSelector.objects.filter(
            group__in=self.roles,
            tables__data_source=self.datasource).first()
        if group_tables_object:
            group_tables = group_tables_object.tables.all()
            all_group_tables = global_tables.union(group_tables)
            # Using subquery to allow filtering after union
            all_group_tables = models.Table.objects.filter(
                id__in=all_group_tables.values('id'))
        else:
            all_group_tables = global_tables
        return all_group_tables

    def get_all_group_columns(self, tables):
        tables_ids = list(tables.values_list('id', flat=True))
        # Get all columns for the tables
        table_columns = models.TableColumn.objects.filter(table_id__in=tables_ids)
        # Get private columns for tables
        private_columns_object = models.PrivateColumnSelector.objects.filter(
            data_source=self.datasource).first()
        if private_columns_object:
            private_columns_ids = private_columns_object.columns.all().values_list('id', flat=True)
            table_columns = table_columns.exclude(id__in=private_columns_ids)

        # Add columns accessible by the user's groups
        group_columns_object = models.GroupColumnSelector.objects.filter(
            group__in=self.roles,
            columns__table__in=tables).first()
        if group_columns_object:
            group_columns = group_columns_object.columns.all()
            all_table_columns = table_columns.union(group_columns)
            # Using subquery to allow filtering after union
            all_table_columns = models.TableColumn.objects.filter(
                id__in=all_table_columns.values('id'))
        else:
            all_table_columns = table_columns
        return all_table_columns
