#!/bin/bash

set -e

echo "Deploying Vulnerable Agent Application to kind-ai-spm cluster..."

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

echo "1. Building Docker images..."
./build.sh

echo "2. Loading images into kind-ai-spm cluster..."
kind load docker-image vulnerable-agent/api-gateway:latest --name ai-spm
kind load docker-image vulnerable-agent/agent-orchestrator:latest --name ai-spm
kind load docker-image vulnerable-agent/task-agent:latest --name ai-spm
kind load docker-image vulnerable-agent/data-agent:latest --name ai-spm
kind load docker-image vulnerable-agent/tool-executor:latest --name ai-spm
kind load docker-image vulnerable-agent/data-pipeline:latest --name ai-spm
kind load docker-image vulnerable-agent/ml-service:latest --name ai-spm

echo "3. Creating namespace..."
kubectl apply -f k8s/namespace.yaml

echo "4. Deploying Redis..."
kubectl apply -f k8s/redis.yaml

echo "5. Deploying PostgreSQL..."
kubectl apply -f k8s/postgres.yaml

echo "6. Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n agent-test --timeout=120s
kubectl wait --for=condition=ready pod -l app=postgres -n agent-test --timeout=120s

sleep 10

echo "7. Deploying application services..."
kubectl apply -f k8s/api-gateway.yaml
kubectl apply -f k8s/agent-orchestrator.yaml
kubectl apply -f k8s/task-agent.yaml
kubectl apply -f k8s/data-agent.yaml
kubectl apply -f k8s/tool-executor.yaml
kubectl apply -f k8s/data-pipeline.yaml
kubectl apply -f k8s/ml-service.yaml

echo "8. Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/api-gateway -n agent-test --timeout=180s
kubectl wait --for=condition=available deployment/agent-orchestrator -n agent-test --timeout=180s
kubectl wait --for=condition=available deployment/task-agent -n agent-test --timeout=180s
kubectl wait --for=condition=available deployment/data-agent -n agent-test --timeout=180s
kubectl wait --for=condition=available deployment/tool-executor -n agent-test --timeout=180s
kubectl wait --for=condition=available deployment/data-pipeline -n agent-test --timeout=180s
kubectl wait --for=condition=available deployment/ml-service -n agent-test --timeout=180s

echo ""
echo "================================================"
echo "Deployment Complete!"
echo "================================================"
echo ""
echo "Checking deployment status..."
kubectl get all -n agent-test

echo ""
echo "Access the API Gateway at:"
echo "  NodePort: kubectl get svc api-gateway -n agent-test"
echo ""
echo "Port forward for local access:"
echo "  kubectl port-forward -n agent-test svc/api-gateway 8000:8000"
echo ""
echo "Test the deployment:"
echo "  curl http://localhost:8000/"
echo ""

