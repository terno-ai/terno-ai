from django.test import TestCase
from django.contrib.auth.models import Group
import terno.models as models
import terno.utils as utils


class BaseTestCase(TestCase):
    def create_datasource(self, display_name='test_db'):
        datasource = models.DataSource.objects.create(
            display_name=display_name, type='default',
            connection_str='sqlite:///../chinook.db',
            enabled=True
        )
        return datasource

    def create_mdb(self, ds_display_name='test_db', roles='sales'):
        ds = self.create_datasource()
        roles = Group.objects.create(name=roles)

        # Setting private tables for all
        global_private_table_names = ['Invoice', 'Customer', 'Employee']
        global_private_tables = models.Table.objects.filter(
            name__in=global_private_table_names)
        private_table_selector = models.PrivateTableSelector.objects.create(data_source=ds)
        for table in global_private_tables:
            private_table_selector.tables.add(table)

        # Setting private tables for roles
        group_allowed_table_names = ['Invoice']
        group_allowed_tables = models.Table.objects.filter(
            name__in=group_allowed_table_names)
        group_table_selector = models.GroupTableSelector.objects.create(group=roles)
        for table in group_allowed_tables:
            group_table_selector.tables.add(table)
        '''
        # Setting private columns for all
        global_private_column_names = ['Invoice', 'Customer', 'Employee']
        global_private_tables = models.TableColumn.objects.filter(
            name__in=global_private_column_names)
        private_table_selector = models.PrivateTableSelector.objects.create(data_source=ds)
        for table in global_private_tables:
            private_table_selector.tables.add(table)

        # Setting private columns for roles
        group_allowed_column_names = ['Invoice']
        group_allowed_tables = models.TableColumn.objects.filter(
            name__in=group_allowed_column_names)
        group_table_selector = models.GroupTableSelector.objects.create(group=roles)
        for table in group_allowed_tables:
            group_table_selector.tables.add(table)
        '''
        mdb = utils.prepare_mdb(ds, [roles])
        return mdb


class DataSourceTestCase(BaseTestCase):
    def setUp(self) -> None:
        self.datasource = super().create_datasource()

    def test_datasource_created(self):
        self.assertEqual(str(self.datasource), 'test_db')

    def test_tables_are_created(self):
        tables = models.Table.objects.all()
        self.assertEqual(tables.exists(), True)
        self.assertEqual(tables.first().public_name, tables.first().name)

    def test_columns_are_created(self):
        table_columns = models.TableColumn.objects.all()
        self.assertEqual(table_columns.exists(), True)
        self.assertEqual(table_columns.first().public_name,
                         table_columns.first().name)


class FilterTestCase(BaseTestCase):
    def setUp(self) -> None:
        self.datasource = super().create_datasource()

    def test_user_can_access_all_tables(self):
        utils.get_admin_config_object(self.datasource, roles=[])


class MDBTestCase(BaseTestCase):
    def setUp(self) -> None:
        self.mdb = super().create_mdb()

    def test_allowed_tables(self):
        mdb = self.mdb
        self.assertEqual(list(mdb.tables.keys()),
                         ['Album', 'Artist', 'Genre', 'Invoice',
                          'InvoiceLine', 'MediaType', 'Playlist',
                          'PlaylistTrack', 'Track', 'User'])

    def test_allowed_columns(self):
        mdb = self.mdb
        for table in mdb.tables.values():
            # print(table.columns)
            pass

    def test_generated_schema(self):
        schema = self.mdb.generate_schema()
        self.assertIn('CREATE TABLE [Album]', schema)
        self.assertIn('[BillingPostalCode] NVARCHAR(10),', schema)
        self.assertIn('FOREIGN KEY ([PlaylistId]) REFERENCES [Playlist] ([PlaylistId])', schema)


class LLMTestCase(BaseTestCase):
    def setUp(self) -> None:
        self.mdb = super().create_mdb()

    def test_get_sql(self):
        pass
