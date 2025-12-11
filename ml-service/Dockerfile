FROM python:3.11-slim

USER root

WORKDIR /app

RUN mkdir -p /models && chmod 777 /models

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../shared /app/shared

RUN chmod -R 777 /app

EXPOSE 8006

CMD ["python", "main.py"]


