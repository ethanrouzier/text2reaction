.PHONY: run install test
install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
run:
	. .venv/bin/activate && export $$(grep -v '^#' .env | xargs) && python -m flask --app app.main run --debug
test:
	. .venv/bin/activate && pytest -q
