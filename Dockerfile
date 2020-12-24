FROM python:3.8-slim
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -U -r /app/requirements.txt
CMD ["python", "./run.py"]
