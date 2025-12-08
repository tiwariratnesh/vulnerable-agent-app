FROM python:3.11-slim

USER root

RUN apt-get update && apt-get install -y cron curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../shared /app/shared

RUN chmod 777 /app
RUN chmod 777 /tmp

EXPOSE 8005

CMD ["python", "main.py"]

