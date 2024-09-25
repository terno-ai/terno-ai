from sqlshield.models import MDatabase
import terno.models as models

class MDBPreparer:
    def __init__(self, datasource, roles):
        self.datasource = datasource
        self.roles = roles
        self.allowed_tables = None
        self.allowed_columns = None
        self.mdb = None

    def prepare(self):
        self._get_admin_config_object()
        self._generate_mdb()
        self._keep_only_tables()
        self._keep_only_columns()
        self._update_table_descriptions()
        self._update_filters()
        return self.mdb

    def _get_admin_config_object(self):
        all_group_tables = _get_all_group_tables(datasource, roles)
        group_columns = _get_all_group_columns(datasource, all_group_tables, roles)
        return all_group_tables, group_columns

    def _generate_mdb(self):
        # Implementation of generate_mdb

    def _keep_only_tables(self):
        # Implementation to keep only allowed tables

    def _keep_only_columns(self):
        # Implementation of keep_only_columns

    def _update_table_descriptions(self):
        # Implementation of update_table_descriptions

    def _update_filters(self):
        # Implementation of update_filters

    def _get_base_filters(self):
        # Implementation of _get_base_filters

    def _get_grp_filters(self):
        # Implementation of _get_grp_filters

    def _merge_grp_filters(self, tbl_base_filters, tbls_grp_filter):
        # Implementation of _merge_grp_filters