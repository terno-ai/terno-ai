from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import suggestions.tasks as tasks


@csrf_exempt
def get_table_and_column_description(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            datasource_id = data.get('datasource_id')
            org_id = data.get('org_id', None)
            input_table_names = data.get('input_table_names', None)
            update_model = data.get('update_model', True)
            overwrite = data.get('overwrite', False)

            if not datasource_id:
                return JsonResponse({'error': 'Missing datasource'}, status=400)

            # Queue the Celery task instead of running it synchronously
            tasks.generate_table_and_column_descriptions_task.delay(
                datasource_id=datasource_id,
                org_id=org_id,
                input_table_names=input_table_names,
                update_model=update_model,
                overwrite=overwrite
            )

            return JsonResponse({'status': 'Task queued. Descriptions will take time to generate.'}, status=202)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
