.PHONY: install run test static

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. .venv/bin/activate && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

test:
	. .venv/bin/activate && PYTHONPATH=. pytest -q

static:
	python3 -m http.server 8001 --directory app/static
