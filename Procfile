web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
worker: celery -A src.api.tasks.celery_app worker --loglevel=info
