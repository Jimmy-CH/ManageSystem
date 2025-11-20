from celery import shared_task

Index = 'operate-log-record'

"celery tasks"


@shared_task
def audit_save_log_task(log):
    print(Index, log)


@shared_task
def audit_delete_log_task(log):
    print(Index, log)

