from celery import Celery
from app.extensions import db
from flask import Flask
import os

# the celery app must use the same database and config as the web flask app
### Create flask instance for celery app
def create_celery_app():
    app = Flask(__name__)

    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        from app.prodConfig import ProdConfig
        app.config.from_object(ProdConfig)
    else:
        from app.config import DevConfig
        app.config.from_object(DevConfig)

    db.init_app(app)

    return app

celery_app = create_celery_app()

celery = Celery(
    'celeryWorker',
    broker=celery_app.config['BROKER_URL'],
    backend=celery_app.config['RESULT_BACKEND'],
)

celery.conf.update(broker_connection_retry_on_startup=True)
celery.autodiscover_tasks(['app.celery_tasks'], force=True)

