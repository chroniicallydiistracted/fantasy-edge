FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt || true
EXPOSE 8001
CMD ["python", "tasks.py"]
