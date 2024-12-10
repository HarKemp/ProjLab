from celery import Celery
from app.extensions import db
from flask import Flask
import os

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

def create_celery_app():
    app = Flask(__name__)

    # Set up config just like in create_app
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        from app.prodConfig import ProdConfig
        app.config.from_object(ProdConfig)
    else:
        from app.config import DevConfig
        app.config.from_object(DevConfig)

    # Initialize the database with the app
    db.init_app(app)

    return app

celery_app = create_celery_app()

celery = Celery(
    'celerypr',
    broker="redis://127.0.0.1:6379/0",
    # backend=app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    backend="redis://127.0.0.1:6379/0",
)

celery.conf.update(broker_connection_retry_on_startup=True)
celery.autodiscover_tasks(['app.tasks'], force=True)

# if __name__ == '__main__':
#     celery.start()


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
