# gets the virtual environment ready for the backend
setup:
	python3 -m venv .venv
	. .venv/bin/activate; pip install -r requirements.txt

run:
	. .venv/bin/activate; gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app

.PHONY: openapi
openapi:
	. .venv/bin/activate; PYTHONPATH=. SKIP_DATA_INIT=1 python scripts/generate_openapi.py
