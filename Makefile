build:
	pip install -r requirements.txt

start:
	pipenv run python run.py

test:
	pip install -r test_requirements.txt ; \
	pytest --cov=sdx-worker tests/

