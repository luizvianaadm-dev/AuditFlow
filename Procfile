web: uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
worker: celery -A src.api.tasks.celery_app worker --loglevel=info --max-tasks-per-child=100 --max-memory-per-child=512000 --concurrency=2
