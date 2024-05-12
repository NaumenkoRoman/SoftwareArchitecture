# facade_service Dockerfile
FROM python:3.9-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["sh", "-c", "python register_service.py && uvicorn main:app --host 0.0.0.0 --port $SERVICE_PORT"]
