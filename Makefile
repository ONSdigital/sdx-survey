build:
	pipenv install
start:
	pipenv run python run.py
test:
	pipenv install --dev ; \
	pipenv run pytest -v --cov-report term-missing --cov=app tests/
