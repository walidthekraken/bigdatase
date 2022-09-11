from celery import Celery

app = Celery("bigse.celery")
app.config_from_object("bigse.celery._config")
