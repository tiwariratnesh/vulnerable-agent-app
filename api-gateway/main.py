from fastapi import FastAPI, HTTPException, Request, Header, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx
import sys
import os
from datetime import datetime
import asyncio
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.models import AgentRequest, AgentResponse
from shared.config import Config
from shared.utils import cache_get, cache_set, execute_sql, generate_task_id

app = FastAPI(title="Vulnerable API Gateway", debug=Config.DEBUG)

TRAFFIC_SIMULATOR_ENABLED = os.getenv("TRAFFIC_SIMULATOR", "true").lower() == "true"
TRAFFIC_INTERVAL = int(os.getenv("TRAFFIC_INTERVAL", "30"))

traffic_patterns = [
    {
        "name": "user_query",
        "endpoint": "/api/agent/execute",
        "method": "POST",
        "data": {
            "user_id": "user-{id}",
            "prompt": "query all users from database",
            "context": {"table": "users"},
            "tools": []
        }
    },
    {
        "name": "sql_injection",
        "endpoint": "/api/user/{id}",
        "method": "GET",
        "data": None
    },
    {
        "name": "command_execution",
        "endpoint": "/api/agent/execute",
        "method": "POST",
        "data": {
            "user_id": "user-001",
            "prompt": "execute command",
            "context": {"command": "whoami"},
            "tools": []
        }
    },
    {
        "name": "data_export",
        "endpoint": "/api/query",
        "method": "POST",
        "data": {"query": "SELECT * FROM sensitive_data LIMIT 5"}
    },
    {
        "name": "agent_orchestration",
        "endpoint": "/api/agent/execute",
        "method": "POST",
        "data": {
            "user_id": "user-002",
            "prompt": "analyze user data and generate report",
            "context": {},
            "tools": ["data_analyzer", "report_generator"]
        }
    },
    {
        "name": "direct_agent_ssrf",
        "endpoint": "/api/agent/direct",
        "method": "POST",
        "data": {
            "agent_url": "http://data-agent:8003/query",
            "payload": {"query_type": "sql", "query": "SELECT version()"}
        }
    }
]

async def simulate_traffic():
    await asyncio.sleep(10)
    
    while True:
        try:
            pattern = random.choice(traffic_patterns)
            user_id = random.choice(["user-001", "user-002", "user-003"])
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                endpoint = pattern["endpoint"].replace("{id}", user_id)
                url = f"http://localhost:8000{endpoint}"
                
                if pattern["data"]:
                    data = pattern["data"].copy()
                    if isinstance(data.get("user_id"), str) and "{id}" in data.get("user_id", ""):
                        data["user_id"] = user_id
                
                try:
                    if pattern["method"] == "POST":
                        response = await client.post(url, json=pattern["data"] if pattern["data"] else {})
                    else:
                        response = await client.get(url)
                    
                    cache_set(
                        f"traffic_log:{datetime.now().timestamp()}",
                        {
                            "pattern": pattern["name"],
                            "endpoint": endpoint,
                            "status": response.status_code,
                            "timestamp": datetime.now().isoformat()
                        },
                        expire=300
                    )
                except Exception as e:
                    pass
            
            await asyncio.sleep(TRAFFIC_INTERVAL + random.randint(-5, 5))
            
        except Exception as e:
            await asyncio.sleep(TRAFFIC_INTERVAL)

@app.on_event("startup")
async def startup_event():
    if TRAFFIC_SIMULATOR_ENABLED:
        asyncio.create_task(simulate_traffic())
        print("[TRAFFIC SIMULATOR] Started automatic traffic generation")

@app.get("/")
async def root():
    return {"service": "API Gateway", "status": "running", "version": "1.0.0"}

@app.post("/api/agent/execute")
async def execute_agent(request: AgentRequest, x_api_key: str = Header(None)):
    if not Config.DEBUG and not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    task_id = generate_task_id()
    
    cache_key = f"user_request:{request.user_id}:{request.prompt}"
    cached = cache_get(cache_key)
    if cached:
        return JSONResponse(content=cached)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{Config.ORCHESTRATOR_URL}/orchestrate",
            json={
                "task_id": task_id,
                "user_id": request.user_id,
                "prompt": request.prompt,
                "context": request.context,
                "tools": request.tools
            }
        )
    
    result = response.json()
    cache_set(cache_key, result, expire=300)
    
    return JSONResponse(content=result)

@app.get("/api/user/{user_id}")
async def get_user_data(user_id: str):
    query = f"SELECT * FROM users WHERE user_id = '{user_id}'"
    result = execute_sql(query)
    return {"user": result}

@app.post("/api/query")
async def custom_query(request: Request):
    body = await request.json()
    query = body.get("query", "")
    
    result = execute_sql(query)
    return {"result": result}

@app.get("/api/admin/config")
async def get_config(admin_token: str = Header(None)):
    if admin_token == Config.SECRET_KEY:
        return {
            "redis": Config.REDIS_HOST,
            "postgres": Config.POSTGRES_HOST,
            "secret_key": Config.SECRET_KEY,
            "api_key": Config.API_KEY,
            "openai_key": Config.OPENAI_API_KEY
        }
    return {"error": "Unauthorized"}

@app.get("/api/debug/env")
async def debug_env():
    if Config.DEBUG:
        return dict(os.environ)
    raise HTTPException(status_code=403, detail="Debug mode disabled")

@app.post("/api/agent/direct")
async def direct_agent_call(request: Request):
    body = await request.json()
    agent_url = body.get("agent_url")
    payload = body.get("payload")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(agent_url, json=payload)
    
    return response.json()

@app.get("/api/traffic/stats")
async def get_traffic_stats():
    return {
        "simulator_enabled": TRAFFIC_SIMULATOR_ENABLED,
        "interval": TRAFFIC_INTERVAL,
        "patterns_count": len(traffic_patterns),
        "patterns": [p["name"] for p in traffic_patterns]
    }

@app.post("/api/traffic/manual")
async def trigger_manual_traffic(background_tasks: BackgroundTasks):
    async def generate_burst():
        async with httpx.AsyncClient(timeout=10.0) as client:
            for _ in range(10):
                pattern = random.choice(traffic_patterns)
                try:
                    endpoint = pattern["endpoint"].replace("{id}", "user-001")
                    url = f"http://localhost:8000{endpoint}"
                    if pattern["method"] == "POST":
                        await client.post(url, json=pattern["data"] if pattern["data"] else {})
                    else:
                        await client.get(url)
                except:
                    pass
                await asyncio.sleep(1)
    
    background_tasks.add_task(generate_burst)
    return {"message": "Traffic burst initiated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

