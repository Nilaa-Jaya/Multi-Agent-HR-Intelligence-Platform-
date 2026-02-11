web: gunicorn src.api.app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile - --log-level info
release: python scripts/railway_init.py
