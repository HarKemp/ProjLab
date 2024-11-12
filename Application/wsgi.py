from app.__init__ import create_app
# from app.celery_worker import make_celery

app = create_app()

# # celery.conf.update(app.config)
# make_celery(app)

if __name__ == "__main__":
    app.run()
