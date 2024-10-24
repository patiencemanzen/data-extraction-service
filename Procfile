web: python -m gunicorn data_extraction_service.asgi:application -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8080
worker: celery -A data_extraction_service worker --loglevel=info --concurrency=2