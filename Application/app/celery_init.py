from celery import Celery
from app.__init__ import db
from flask import Flask
import os
from dotenv import load_dotenv

# the celery app must use the same database and config as the web flask app
### Create flask instance for celery app
def create_celery_app():
    load_dotenv()

    app = Flask(__name__)

    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        from app.prodConfig import ProdConfig
        app.config.from_object(ProdConfig)
    else:
        from app.config import DevConfig
        app.config.from_object(DevConfig)

    sqlalchemy_database_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
    if sqlalchemy_database_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlalchemy_database_uri

    db.init_app(app)

    return app

celery_app = create_celery_app()

redis_url = os.environ.get('REDIS_URL')
celery = Celery(
    'celeryWorker',
    broker = redis_url if redis_url else celery_app.config['BROKER_URL'],
    backend = redis_url if redis_url else celery_app.config['RESULT_BACKEND'],
)

celery.conf.update(broker_connection_retry_on_startup=True)
celery.autodiscover_tasks(['app.celery_tasks'], force=True)

