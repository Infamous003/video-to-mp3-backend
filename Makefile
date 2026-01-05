.PHONY: run/app
run/app:
	uvicorn app.main:app --reload

.PHONY: run/celery
run/celery:
	celery -A app.workers.celery_app:celery_app worker --loglevel=info