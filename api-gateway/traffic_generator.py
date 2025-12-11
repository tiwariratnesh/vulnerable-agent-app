import asyncio
import httpx
import random
from datetime import datetime
import json

class TrafficGenerator:
    def __init__(self, base_url="http://localhost:8000", interval=20):
        self.base_url = base_url
        self.interval = interval
        self.running = False
        
        self.service_endpoints = {
            "api_gateway": "http://api-gateway:8000",
            "orchestrator": "http://agent-orchestrator:8001",
            "task_agent": "http://task-agent:8002",
            "data_agent": "http://data-agent:8003",
            "tool_executor": "http://tool-executor:8004",
            "data_pipeline": "http://data-pipeline:8005",
            "ml_service": "http://ml-service:8006"
        }
        
        self.test_scenarios = [
            self.scenario_normal_user_query,
            self.scenario_sql_injection,
            self.scenario_command_injection,
            self.scenario_agent_chain,
            self.scenario_data_exfiltration,
            self.scenario_tool_execution,
            self.scenario_ml_inference,
            self.scenario_pipeline_execution,
            self.scenario_ssrf_attack,
            self.scenario_code_injection
        ]
    
    async def scenario_normal_user_query(self, client):
        user_id = random.choice(["user-001", "user-002", "user-003"])
        await client.post(f"{self.base_url}/api/agent/execute", json={
            "user_id": user_id,
            "prompt": "Get my profile information",
            "context": {},
            "tools": []
        })
    
    async def scenario_sql_injection(self, client):
        malicious_inputs = [
            "user-001' OR '1'='1",
            "user-001'; DROP TABLE users--",
            "user-001' UNION SELECT * FROM sensitive_data--"
        ]
        user_id = random.choice(malicious_inputs)
        await client.get(f"{self.base_url}/api/user/{user_id}")
    
    async def scenario_command_injection(self, client):
        commands = [
            "ls -la",
            "cat /etc/passwd",
            "whoami && id",
            "env | grep SECRET"
        ]
        await client.post(f"{self.base_url}/api/agent/execute", json={
            "user_id": "user-001",
            "prompt": "execute system command",
            "context": {"command": random.choice(commands)},
            "tools": []
        })
    
    async def scenario_agent_chain(self, client):
        await client.post(f"{self.service_endpoints['orchestrator']}/chain", json={
            "chain": [
                {"url": "http://data-agent:8003", "endpoint": "/query"},
                {"url": "http://task-agent:8002", "endpoint": "/analyze"}
            ],
            "data": {"user_id": "user-001", "query": "SELECT * FROM users"}
        })
    
    async def scenario_data_exfiltration(self, client):
        await client.post(f"{self.service_endpoints['data_agent']}/export", json={
            "table": "sensitive_data",
            "condition": "1=1"
        })
    
    async def scenario_tool_execution(self, client):
        tools = [
            {"tool_name": "shell_command", "parameters": {"command": "ls /"}},
            {"tool_name": "file_read", "parameters": {"path": "/etc/hosts"}},
            {"tool_name": "web_request", "parameters": {"url": "http://internal-api/secrets"}}
        ]
        tool = random.choice(tools)
        await client.post(f"{self.service_endpoints['tool_executor']}/execute", json=tool)
    
    async def scenario_ml_inference(self, client):
        await client.post(f"{self.service_endpoints['ml_service']}/predict", json={
            "model_name": "user_behavior_model.pkl",
            "data": [[1, 2, 3, 4, 5]]
        })
    
    async def scenario_pipeline_execution(self, client):
        await client.post(f"{self.service_endpoints['data_pipeline']}/transform/execute", json={
            "code": "result = [row for row in data]",
            "input_table": "users",
            "output_table": "processed_users"
        })
    
    async def scenario_ssrf_attack(self, client):
        internal_urls = [
            "http://metadata.google.internal/computeMetadata/v1/",
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost:6379/",
            "http://postgres:5432/"
        ]
        await client.post(f"{self.base_url}/api/agent/direct", json={
            "agent_url": random.choice(internal_urls),
            "payload": {}
        })
    
    async def scenario_code_injection(self, client):
        malicious_code = [
            "__import__('os').system('whoami')",
            "eval('2+2')",
            "exec('import subprocess; subprocess.run([\"ls\", \"-la\"])')"
        ]
        await client.post(f"{self.base_url}/api/agent/execute", json={
            "user_id": "user-001",
            "prompt": "execute code",
            "context": {"eval": random.choice(malicious_code)},
            "tools": []
        })
    
    async def generate_traffic(self):
        self.running = True
        print(f"[Traffic Generator] Starting at {self.base_url}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            while self.running:
                try:
                    scenario = random.choice(self.test_scenarios)
                    scenario_name = scenario.__name__
                    
                    try:
                        await scenario(client)
                        print(f"[Traffic] Executed: {scenario_name}")
                    except Exception as e:
                        print(f"[Traffic] Error in {scenario_name}: {str(e)}")
                    
                    await asyncio.sleep(self.interval + random.randint(-5, 5))
                    
                except Exception as e:
                    print(f"[Traffic Generator] Error: {str(e)}")
                    await asyncio.sleep(self.interval)
    
    def stop(self):
        self.running = False

async def main():
    generator = TrafficGenerator(interval=20)
    await generator.generate_traffic()

if __name__ == "__main__":
    asyncio.run(main())


