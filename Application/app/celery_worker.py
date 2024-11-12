from celery import Celery
from wsgi import app

def make_celery(app):
    celery = Celery(
        'app',
        backend='redis://localhost:6379/0',
        broker='redis://localhost:6379/0'
    )

    if app:
        celery.conf.update(app.config)
        # Ensure tasks run within Flask's application context
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return super().__call__(*args, **kwargs)

        celery.Task = ContextTask

    return celery

celery = make_celery(app)