from celery import Celery


# celery = Celery()
# def make_celery(app):
#
#     celery = Celery(
#         app.import_name,
#         broker=app.config.get("broker_url", "redis://localhost:6379/0"),
#         # backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
#         backend=app.config.get("result_backend", "redis://localhost:6379/0"),
#     )
#
#     celery.conf.update(app.config)
#     celery.conf.update(broker_connection_retry_on_startup=True)
#     celery.autodiscover_tasks(['app.tasks'], force=True)
#
#     return celery

celery = Celery(
    'celerypr',
    broker="redis://localhost:6379/0",
    # backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    backend="redis://localhost:6379/0",
)

celery.conf.update(broker_connection_retry_on_startup=True)
celery.autodiscover_tasks(['app.tasks'], force=True)

if __name__ == '__main__':
    celery.start()


# celery = Celery(
#     app.import_name,
#     broker="redis://localhost:6379/0",
#     # backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
#     backend="redis://localhost:6379/0",
# )
#
# celery.conf.update(app.config)
# celery.conf.update(broker_connection_retry_on_startup=True)
# celery.autodiscover_tasks(['app.tasks'], force=True)
