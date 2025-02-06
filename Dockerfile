FROM europe-west2-docker.pkg.dev/ons-sdx-ci/sdx-apps/sdx-gcp:1.4.4 
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "./run.py"]
