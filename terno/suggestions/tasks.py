from celery import shared_task
import suggestions.utils as utils
import logging
logger = logging.getLogger(__name__)


@shared_task
def generate_table_and_column_descriptions_task(datasource_id, input_table_names=None, update_model=True, overwrite=False):
    """
    Celery task to generate table and column descriptions asynchronously.
    """
    logger.info(f'Starting Celery task for datasource {datasource_id} on tables {input_table_names}')
    utils.generate_table_and_column_description(
        datasource_id=datasource_id,
        input_table_names=input_table_names,
        update_model=update_model,
        overwrite=overwrite
    )
    logger.info(f'Celery task to generate table and column descriptions succeded for datasource {datasource_id} tables {input_table_names}.')
