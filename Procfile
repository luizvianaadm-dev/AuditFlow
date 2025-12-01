web: alembic upgrade head && gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
worker: celery -A src.api.tasks.celery_app worker --loglevel=info
