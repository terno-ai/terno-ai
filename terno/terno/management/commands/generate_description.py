from django.core.management.base import BaseCommand, CommandError
from terno.models import DataSource, Table
from suggestions.tasks import generate_table_and_column_descriptions_task


class Command(BaseCommand):
    help = 'Trigger table & column description generation for a DataSource.'

    def add_arguments(self, parser):
        parser.add_argument('datasource_id', type=int, help='ID of the DataSource to describe')
        parser.add_argument('--tables', nargs='*', type=str, help='Optional: List of table names to process')
        parser.add_argument('--not-update-model', action='store_true', help='Optional: If passed, the Table and Column models will NOT be updated.')
        parser.add_argument('--overwrite', action='store_true', help='Optional: Overwrite existing descriptions')

    def handle(self, *args, **options):
        datasource_id = options['datasource_id']
        table_names = options.get('tables', None)
        overwrite = options.get('overwrite', False)
        update_model = not options.get('not_update_model', False)

        try:
            datasource = DataSource.objects.get(id=datasource_id)
        except DataSource.DoesNotExist:
            raise CommandError(f'DataSource with ID {datasource_id} does not exist.')

        task = generate_table_and_column_descriptions_task.delay(
            datasource_id=datasource_id,
            input_table_names=table_names,
            update_model=update_model,
            overwrite=overwrite
        )

        self.stdout.write(self.style.SUCCESS(
            f'Task queued for DataSource {datasource_id} (Task ID: {task.id}).'
        ))
