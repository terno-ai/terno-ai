from celery import shared_task


@shared_task
def add_num(x, y):
    print(f'Adding {x} and {y}')
    return x + y
