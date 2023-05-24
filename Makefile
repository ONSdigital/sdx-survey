.PHONY: build
build:
	pip install -r requirements.txt

.PHONY: start
start: build
	python run.py

.PHONY: test
test: build
	pip install -r test-requirements.txt
	flake8
	pytest -v --cov-report term-missing --disable-warnings --cov=app tests/
