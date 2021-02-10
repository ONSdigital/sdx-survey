start:
	pipenv run python run.py

test:
	pip install pytest ; \
	pytest --override-ini  "testpaths=tests"

build:
	pip install -r requirements.txt
