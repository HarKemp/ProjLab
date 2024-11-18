from app.__init__ import create_app, ext_celery

app = create_app()
celery = ext_celery.celery

print("wsgi celery broker url: ", celery.conf.broker_url)

if __name__ == "__main__":
    app.run()
