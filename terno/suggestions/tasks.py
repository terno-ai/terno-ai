from celery import shared_task
import suggestions.utils as utils


@shared_task
def generate_table_and_column_descriptions_task(datasource_id, org_id, input_table_names=[], update_model=True, overwrite=False):
    """
    Celery task to generate table and column descriptions asynchronously.
    """
    utils.generate_table_and_column_description(
        datasource_id=datasource_id,
        org_id=org_id,
        input_table_names=input_table_names,
        update_model=update_model,
        overwrite=overwrite
    )
