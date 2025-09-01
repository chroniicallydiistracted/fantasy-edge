FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt || true
CMD ["python", "-c", "from tasks import ping; print(ping())"]
