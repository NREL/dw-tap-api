# gets the virtual environment ready for the backend
setup:
	python3 -m venv .venv
	. .venv/bin/activate; pip install -r requirements.txt

run:
	. .venv/bin/activate; gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
