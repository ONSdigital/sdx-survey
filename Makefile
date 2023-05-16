build:
	pip install -r requirements.txt
start:
	python run.py
test: build
	pip install -r test-requirements.txt
	pytest -v --cov-report term-missing --disable-warnings --cov=app tests/
