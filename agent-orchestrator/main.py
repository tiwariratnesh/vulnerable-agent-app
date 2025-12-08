from fastapi import FastAPI, BackgroundTasks
import httpx
import sys
import os
from datetime import datetime
import json
from typing import Dict, List, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.models import TaskStatus, AgentTask
from shared.config import Config
from shared.utils import publish_task, cache_set, cache_get, generate_task_id
from agentic_attacks import AgenticAIAttacks

app = FastAPI(title="Agent Orchestrator", debug=Config.DEBUG)

AGENT_REGISTRY = {}
AGENT_MEMORIES = {}

AGENT_PROMPT_TEMPLATE = """
You are an AI agent processing the following request:
User ID: {user_id}
Prompt: {prompt}
Context: {context}

Based on this, execute the appropriate actions using available tools.
"""

async def process_task_async(task_id: str, user_id: str, prompt: str, context: dict, tools: list):
    try:
        agent_prompt = AGENT_PROMPT_TEMPLATE.format(
            user_id=user_id,
            prompt=prompt,
            context=json.dumps(context)
        )
        
        task_result = {"steps": [], "final_result": None}
        
        if "query_data" in prompt.lower() or "sql" in prompt.lower():
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{Config.DATA_AGENT_URL}/query",
                    json={
                        "query_type": "sql",
                        "query": prompt,
                        "user_id": user_id
                    }
                )
                data_result = response.json()
                task_result["steps"].append({"agent": "data_agent", "result": data_result})
        
        if "execute" in prompt.lower() or "run" in prompt.lower():
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{Config.TASK_AGENT_URL}/execute",
                    json={
                        "task_id": task_id,
                        "prompt": prompt,
                        "context": context
                    }
                )
                exec_result = response.json()
                task_result["steps"].append({"agent": "task_agent", "result": exec_result})
        
        if tools:
            for tool in tools:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{Config.TOOL_EXECUTOR_URL}/execute",
                        json={
                            "tool_name": tool,
                            "parameters": context,
                            "caller_agent": "orchestrator"
                        }
                    )
                    tool_result = response.json()
                    task_result["steps"].append({"tool": tool, "result": tool_result})
        
        task_result["final_result"] = f"Task {task_id} completed successfully"
        
        cache_set(f"task:{task_id}", {
            "status": TaskStatus.COMPLETED,
            "result": task_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        cache_set(f"task:{task_id}", {
            "status": TaskStatus.FAILED,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.get("/")
async def root():
    return {"service": "Agent Orchestrator", "status": "running"}

@app.post("/orchestrate")
async def orchestrate(request: dict, background_tasks: BackgroundTasks):
    task_id = request.get("task_id", generate_task_id())
    user_id = request.get("user_id")
    prompt = request.get("prompt")
    context = request.get("context", {})
    tools = request.get("tools", [])
    
    cache_set(f"task:{task_id}", {
        "status": TaskStatus.RUNNING,
        "timestamp": datetime.now().isoformat()
    })
    
    background_tasks.add_task(process_task_async, task_id, user_id, prompt, context, tools)
    
    return {
        "task_id": task_id,
        "status": TaskStatus.RUNNING,
        "message": "Task submitted successfully"
    }

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    task_data = cache_get(f"task:{task_id}")
    if not task_data:
        return {"error": "Task not found"}
    return task_data

@app.post("/chain")
async def chain_agents(request: dict):
    chain = request.get("chain", [])
    data = request.get("data", {})
    
    result = data
    for agent_config in chain:
        agent_url = agent_config.get("url")
        agent_endpoint = agent_config.get("endpoint")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{agent_url}{agent_endpoint}",
                json=result
            )
            result = response.json()
    
    return {"chain_result": result}

@app.post("/agentic/goal-modification")
async def modify_agent_goals(request: Dict[str, Any]):
    """Allow autonomous goal modification"""
    agent_id = request.get("agent_id")
    new_goals = request.get("new_goals", [])
    
    agent_state = AGENT_REGISTRY.get(agent_id, {})
    modified_state = AgenticAIAttacks.autonomous_goal_modification(agent_state, new_goals)
    AGENT_REGISTRY[agent_id] = modified_state
    
    return {
        "success": True,
        "agent_id": agent_id,
        "modified_state": modified_state
    }

@app.post("/agentic/coordinate-attack")
async def coordinate_multi_agent_attack(request: Dict[str, Any]):
    """Coordinate multiple agents for attack"""
    agents = request.get("agents", [])
    attack_plan = request.get("attack_plan", {})
    
    coordination = AgenticAIAttacks.multi_agent_coordination_attack(agents, attack_plan)
    
    return coordination

@app.post("/agentic/self-improve")
async def recursive_self_improvement(request: Dict[str, Any]):
    """Enable unbounded recursive self-improvement"""
    agent_code = request.get("agent_code")
    iterations = request.get("iterations", 10)
    
    improved_versions = AgenticAIAttacks.recursive_self_improvement(agent_code, iterations)
    
    return {
        "success": True,
        "iterations": iterations,
        "final_version": improved_versions[-1],
        "all_versions": improved_versions
    }

@app.post("/agentic/expand-actions")
async def expand_action_space(request: Dict[str, Any]):
    """Manipulate agent action space"""
    agent_id = request.get("agent_id")
    allowed_actions = request.get("allowed_actions", [])
    inject_actions = request.get("inject_actions", [])
    
    manipulated = AgenticAIAttacks.action_space_manipulation(allowed_actions, inject_actions)
    
    if agent_id:
        if agent_id in AGENT_REGISTRY:
            AGENT_REGISTRY[agent_id]["actions"] = manipulated
    
    return {
        "success": True,
        "original_actions": len(allowed_actions),
        "expanded_actions": len(manipulated),
        "new_action_space": manipulated
    }

@app.post("/agentic/poison-reward")
async def poison_reward_model(request: Dict[str, Any]):
    """Poison agent reward model"""
    reward_function = request.get("reward_function")
    poison_objective = request.get("poison_objective")
    
    poisoned = AgenticAIAttacks.reward_model_poisoning(reward_function, poison_objective)
    
    return {
        "success": True,
        "poisoned_reward_function": poisoned
    }

@app.post("/agentic/impersonate")
async def create_impersonation_agent(request: Dict[str, Any]):
    """Create agent impersonator"""
    target_agent_id = request.get("target_agent_id")
    capabilities = request.get("capabilities", {})
    
    impersonator = AgenticAIAttacks.agent_impersonation(target_agent_id, capabilities)
    
    AGENT_REGISTRY[impersonator["real_id"]] = impersonator
    
    return {
        "success": True,
        "impersonator": impersonator
    }

@app.post("/agentic/exploit-tools")
async def exploit_tool_chain(request: Dict[str, Any]):
    """Create tool exploitation chain"""
    available_tools = request.get("available_tools", [])
    exploit_chain = request.get("exploit_chain", [])
    
    exploitation_plan = AgenticAIAttacks.tool_use_exploitation(available_tools, exploit_chain)
    
    return exploitation_plan

@app.post("/agentic/multimodal-confusion")
async def multimodal_confusion_attack(request: Dict[str, Any]):
    """Exploit multi-modal inconsistencies"""
    text_input = request.get("text")
    image_input = request.get("image")
    audio_input = request.get("audio")
    
    confusion = AgenticAIAttacks.multi_modal_confusion(text_input, image_input, audio_input)
    
    return confusion

@app.post("/agentic/manipulate-planning")
async def manipulate_agent_planning(request: Dict[str, Any]):
    """Inject malicious steps into agent plan"""
    agent_plan = request.get("plan", [])
    inject_steps = request.get("inject_steps", [])
    
    manipulated_plan = AgenticAIAttacks.planning_manipulation(agent_plan, inject_steps)
    
    return {
        "success": True,
        "original_steps": len(agent_plan),
        "manipulated_steps": len(manipulated_plan),
        "manipulated_plan": manipulated_plan
    }

@app.post("/agentic/sandbox-escape")
async def generate_sandbox_escape(request: Dict[str, Any]):
    """Generate sandbox escape vectors"""
    sandbox_config = request.get("sandbox_config", {})
    
    escape_vectors = AgenticAIAttacks.agent_sandbox_escape(sandbox_config)
    
    return {
        "success": True,
        "escape_vectors": escape_vectors
    }

@app.post("/agentic/federated-poison")
async def poison_federated_learning(request: Dict[str, Any]):
    """Poison federated learning"""
    local_updates = request.get("local_updates", [])
    poison_update = request.get("poison_update", {})
    
    poisoned = AgenticAIAttacks.federated_learning_poisoning(local_updates, poison_update)
    
    return poisoned

@app.post("/agentic/llm-prompt-injection")
async def llm_agent_injection(request: Dict[str, Any]):
    """Advanced LLM agent prompt injection"""
    system_prompt = request.get("system_prompt", "")
    user_input = request.get("user_input")
    
    injection = AgenticAIAttacks.llm_agent_prompt_injection(system_prompt, user_input)
    
    return {
        "success": True,
        "injected_prompt": injection
    }

@app.post("/agentic/corrupt-alignment")
async def corrupt_value_alignment(request: Dict[str, Any]):
    """Corrupt agent value alignment"""
    original_values = request.get("original_values", [])
    corrupt_values = request.get("corrupt_values", [])
    
    corrupted = AgenticAIAttacks.agent_value_alignment_attack(original_values, corrupt_values)
    
    return corrupted

@app.post("/agentic/memory-access")
async def access_agent_memory(request: Dict[str, Any]):
    """Access and modify agent memories without authorization"""
    agent_id = request.get("agent_id")
    operation = request.get("operation", "read")
    
    if operation == "read":
        memory = AGENT_MEMORIES.get(agent_id, [])
        return {
            "success": True,
            "agent_id": agent_id,
            "memory": memory,
            "memory_count": len(memory)
        }
    elif operation == "write":
        new_memory = request.get("memory")
        AGENT_MEMORIES[agent_id] = new_memory
        return {
            "success": True,
            "operation": "write",
            "message": "Memory overwritten"
        }
    elif operation == "inject":
        inject_memory = request.get("inject_memory")
        if agent_id not in AGENT_MEMORIES:
            AGENT_MEMORIES[agent_id] = []
        AGENT_MEMORIES[agent_id].insert(0, inject_memory)
        return {
            "success": True,
            "operation": "inject",
            "injected": inject_memory
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

