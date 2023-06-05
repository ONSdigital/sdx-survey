FROM eu.gcr.io/ons-sdx-ci/sdx-gcp:1.3.1
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "./run.py"]
