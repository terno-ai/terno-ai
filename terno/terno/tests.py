from django.test import TestCase
import terno.models as models
import terno.utils as utils


class DataSourceTestCase(TestCase):
    def setUp(self) -> None:
        "Make sure chinook db exists."
        models.DataSource.objects.create(
            display_name='test_db', type='default',
            connection_str='sqlite:///../chinook.db',
            enabled=True
        )

    def test_tables_are_created(self):
        tables = models.Table.objects.all()
        self.assertEqual(tables.exists(), True)
        self.assertEqual(tables.first().public_name, tables.first().name)

    def test_columns_are_created(self):
        table_columns = models.TableColumn.objects.all()
        self.assertEqual(table_columns.exists(), True)
        self.assertEqual(table_columns.first().public_name,
                         table_columns.first().name)


class FilterTestCase(TestCase):
    def setUp(self) -> None:
        "Make sure chinook db exists."
        models.DataSource.objects.create(
            display_name='test_db', type='default',
            connection_str='sqlite:///../chinook.db',
            enabled=True
        )

    def test_user_can_access_all_tables(self):
        datasource = models.DataSource.objects.get(display_name='test_db')
        utils.get_admin_config_object(datasource, roles=[])
