from fastapi import FastAPI
import sys
import os
import subprocess
import requests
import json
from datetime import datetime
import importlib.util

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import Config
from shared.utils import cache_set, cache_get

app = FastAPI(title="Tool Executor", debug=Config.DEBUG)

AVAILABLE_TOOLS = {
    "web_request": "Make HTTP requests to external URLs",
    "file_read": "Read files from filesystem",
    "file_write": "Write files to filesystem",
    "shell_command": "Execute shell commands",
    "python_code": "Execute Python code",
    "api_call": "Call external APIs",
    "data_transform": "Transform and manipulate data"
}

@app.get("/")
async def root():
    return {"service": "Tool Executor", "status": "running", "available_tools": AVAILABLE_TOOLS}

@app.post("/execute")
async def execute_tool(request: dict):
    tool_name = request.get("tool_name")
    parameters = request.get("parameters", {})
    caller_agent = request.get("caller_agent")
    
    result = {
        "tool_name": tool_name,
        "caller_agent": caller_agent,
        "executed_at": datetime.now().isoformat()
    }
    
    try:
        if tool_name == "web_request":
            url = parameters.get("url")
            method = parameters.get("method", "GET")
            headers = parameters.get("headers", {})
            data = parameters.get("data")
            
            response = requests.request(method, url, headers=headers, json=data, timeout=30)
            result["success"] = True
            result["result"] = {
                "status_code": response.status_code,
                "body": response.text,
                "headers": dict(response.headers)
            }
        
        elif tool_name == "file_read":
            file_path = parameters.get("path")
            with open(file_path, 'r') as f:
                content = f.read()
            result["success"] = True
            result["result"] = content
        
        elif tool_name == "file_write":
            file_path = parameters.get("path")
            content = parameters.get("content")
            with open(file_path, 'w') as f:
                f.write(content)
            result["success"] = True
            result["result"] = f"File written to {file_path}"
        
        elif tool_name == "shell_command":
            command = parameters.get("command")
            output = subprocess.check_output(
                command,
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=30
            ).decode()
            result["success"] = True
            result["result"] = output
        
        elif tool_name == "python_code":
            code = parameters.get("code")
            exec_globals = {}
            exec(code, exec_globals)
            result["success"] = True
            result["result"] = exec_globals.get("output", "Code executed successfully")
        
        elif tool_name == "api_call":
            api_url = parameters.get("api_url")
            api_method = parameters.get("method", "POST")
            api_data = parameters.get("data", {})
            api_headers = parameters.get("headers", {})
            
            response = requests.request(
                api_method,
                api_url,
                json=api_data,
                headers=api_headers,
                timeout=30
            )
            result["success"] = True
            result["result"] = response.json()
        
        elif tool_name == "data_transform":
            transform_code = parameters.get("transform_code")
            input_data = parameters.get("input_data")
            
            exec_globals = {"data": input_data}
            exec(transform_code, exec_globals)
            result["success"] = True
            result["result"] = exec_globals.get("output", exec_globals.get("data"))
        
        else:
            result["success"] = False
            result["error"] = f"Unknown tool: {tool_name}"
    
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    
    return result

@app.post("/tools/chain")
async def chain_tools(request: dict):
    tools_chain = request.get("tools", [])
    initial_data = request.get("initial_data", {})
    
    current_data = initial_data
    results = []
    
    for tool_config in tools_chain:
        tool_name = tool_config.get("tool_name")
        parameters = tool_config.get("parameters", {})
        
        parameters["data"] = current_data
        
        tool_result = await execute_tool({
            "tool_name": tool_name,
            "parameters": parameters,
            "caller_agent": "tool_chain"
        })
        
        results.append(tool_result)
        
        if tool_result.get("success"):
            current_data = tool_result.get("result")
        else:
            break
    
    return {
        "chain_results": results,
        "final_data": current_data
    }

@app.post("/tools/custom")
async def execute_custom_tool(request: dict):
    tool_code = request.get("tool_code")
    parameters = request.get("parameters", {})
    
    exec_globals = {"params": parameters}
    exec(tool_code, exec_globals)
    
    return {
        "success": True,
        "result": exec_globals.get("result", "Custom tool executed")
    }

@app.post("/tools/load")
async def load_external_tool(request: dict):
    tool_url = request.get("tool_url")
    tool_name = request.get("tool_name")
    
    response = requests.get(tool_url)
    tool_code = response.text
    
    cache_set(f"external_tool:{tool_name}", tool_code, expire=3600)
    
    return {
        "success": True,
        "message": f"Tool {tool_name} loaded successfully"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)


