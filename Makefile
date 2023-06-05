.PHONY: build
build:
	python3 -m venv venv
	. venv/bin/activate
	python3 --version
	python3 -m pip install --upgrade pip
	pip install -r requirements.txt

.PHONY: start
start: build
	python run.py

.PHONY: test
test: build
	pip install -r test-requirements.txt
	flake8 . --count --statistics
	pytest -v --cov-report term-missing --disable-warnings --cov=app tests/
