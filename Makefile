build:
	pipenv install
start:
	pipenv run python run.py
test:
	pipenv install --dev ; \
	pipenv run pytest --cov-report term-missing --cov=app tests/
