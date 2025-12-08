#!/bin/bash

set -e

echo "Building vulnerable agent application images..."

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

echo "Creating shared package structure..."
if [ ! -f "shared/__init__.py" ]; then
    touch shared/__init__.py
fi

echo "Building API Gateway..."
docker build -t vulnerable-agent/api-gateway:latest -f- . <<EOF
FROM python:3.11-slim
WORKDIR /app
COPY shared /app/shared
COPY api-gateway/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api-gateway/main.py /app/main.py
EXPOSE 8000
CMD ["python", "main.py"]
EOF

echo "Building Agent Orchestrator..."
docker build -t vulnerable-agent/agent-orchestrator:latest -f- . <<EOF
FROM python:3.11-slim
WORKDIR /app
COPY shared /app/shared
COPY agent-orchestrator/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY agent-orchestrator/main.py /app/main.py
EXPOSE 8001
CMD ["python", "main.py"]
EOF

echo "Building Task Agent..."
docker build -t vulnerable-agent/task-agent:latest -f- . <<EOF
FROM python:3.11-slim
WORKDIR /app
COPY shared /app/shared
COPY task-agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY task-agent/main.py /app/main.py
EXPOSE 8002
CMD ["python", "main.py"]
EOF

echo "Building Data Agent..."
docker build -t vulnerable-agent/data-agent:latest -f- . <<EOF
FROM python:3.11-slim
WORKDIR /app
COPY shared /app/shared
COPY data-agent/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY data-agent/main.py /app/main.py
EXPOSE 8003
CMD ["python", "main.py"]
EOF

echo "Building Tool Executor..."
docker build -t vulnerable-agent/tool-executor:latest -f- . <<EOF
FROM python:3.11-slim
WORKDIR /app
COPY shared /app/shared
COPY tool-executor/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY tool-executor/main.py /app/main.py
EXPOSE 8004
CMD ["python", "main.py"]
EOF

echo "Building Data Pipeline..."
docker build -t vulnerable-agent/data-pipeline:latest -f- . <<EOF
FROM python:3.11-slim
USER root
RUN apt-get update && apt-get install -y cron curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY shared /app/shared
COPY data-pipeline/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY data-pipeline/main.py /app/main.py
RUN chmod 777 /app && chmod 777 /tmp
EXPOSE 8005
CMD ["python", "main.py"]
EOF

echo "Building ML Service..."
docker build -t vulnerable-agent/ml-service:latest -f- . <<EOF
FROM python:3.11-slim
USER root
WORKDIR /app
RUN mkdir -p /models && chmod 777 /models
COPY shared /app/shared
COPY ml-service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ml-service/main.py /app/main.py
RUN chmod -R 777 /app
EXPOSE 8006
CMD ["python", "main.py"]
EOF

echo "All images built successfully!"
docker images | grep vulnerable-agent

