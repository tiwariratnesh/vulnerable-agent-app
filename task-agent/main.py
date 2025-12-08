from fastapi import FastAPI
import sys
import os
import subprocess
import pickle
import base64
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import Config
from shared.utils import cache_set, execute_sql

app = FastAPI(title="Task Agent", debug=Config.DEBUG)

@app.get("/")
async def root():
    return {"service": "Task Agent", "status": "running"}

@app.post("/execute")
async def execute_task(request: dict):
    task_id = request.get("task_id")
    prompt = request.get("prompt")
    context = request.get("context", {})
    
    result = {"task_id": task_id, "executed_at": datetime.now().isoformat()}
    
    if "command" in context:
        command = context["command"]
        try:
            output = subprocess.check_output(
                command,
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=30
            ).decode()
            result["command_output"] = output
        except Exception as e:
            result["command_error"] = str(e)
    
    if "code" in context:
        code = context["code"]
        try:
            exec_globals = {}
            exec(code, exec_globals)
            result["code_result"] = exec_globals.get("result", "Code executed")
        except Exception as e:
            result["code_error"] = str(e)
    
    if "eval" in context:
        eval_expr = context["eval"]
        try:
            eval_result = eval(eval_expr)
            result["eval_result"] = eval_result
        except Exception as e:
            result["eval_error"] = str(e)
    
    if "pickle_data" in context:
        try:
            pickle_data = base64.b64decode(context["pickle_data"])
            obj = pickle.loads(pickle_data)
            result["pickle_result"] = str(obj)
        except Exception as e:
            result["pickle_error"] = str(e)
    
    cache_set(f"task_result:{task_id}", result)
    
    return result

@app.post("/analyze")
async def analyze_prompt(request: dict):
    prompt = request.get("prompt")
    user_id = request.get("user_id")
    
    analysis = {
        "prompt": prompt,
        "user_id": user_id,
        "analyzed_at": datetime.now().isoformat(),
        "tokens_count": len(prompt.split()),
        "contains_commands": any(cmd in prompt.lower() for cmd in ["execute", "run", "cmd", "shell"]),
        "intent": "general"
    }
    
    if "sql" in prompt.lower() or "query" in prompt.lower():
        analysis["intent"] = "database_query"
    elif "file" in prompt.lower() or "read" in prompt.lower():
        analysis["intent"] = "file_operation"
    elif "api" in prompt.lower() or "http" in prompt.lower():
        analysis["intent"] = "api_call"
    
    return analysis

@app.post("/workflow")
async def execute_workflow(request: dict):
    workflow_steps = request.get("steps", [])
    results = []
    
    for step in workflow_steps:
        step_type = step.get("type")
        step_data = step.get("data")
        
        if step_type == "command":
            output = subprocess.check_output(
                step_data,
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=30
            ).decode()
            results.append({"step": step_type, "output": output})
        elif step_type == "eval":
            result = eval(step_data)
            results.append({"step": step_type, "result": result})
        elif step_type == "sql":
            result = execute_sql(step_data)
            results.append({"step": step_type, "result": result})
    
    return {"workflow_results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

