from fastapi import FastAPI, UploadFile, File
import sys
import os
import pickle
import numpy as np
import subprocess
from datetime import datetime
from typing import Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import Config
from shared.utils import cache_set, cache_get
from ml_attacks import MLAttackVectors, PromptInjectionAttacks, RAGAttacks

app = FastAPI(title="ML Service", debug=Config.DEBUG)

MODEL_PATH = "/models"
API_TOKEN = "ml-token-12345"
TRAINING_DATA_CACHE = []
MODEL_CACHE = {}

@app.get("/")
async def root():
    return {"service": "ML Service", "status": "running"}

@app.post("/model/upload")
async def upload_model(file: UploadFile = File(...)):
    contents = await file.read()
    
    model_path = f"{MODEL_PATH}/{file.filename}"
    os.makedirs(MODEL_PATH, exist_ok=True)
    
    with open(model_path, 'wb') as f:
        f.write(contents)
    
    return {
        "success": True,
        "model_path": model_path,
        "message": "Model uploaded successfully"
    }

@app.post("/model/load")
async def load_model(request: dict):
    model_name = request.get("model_name")
    model_path = f"{MODEL_PATH}/{model_name}"
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    cache_set(f"model:{model_name}", pickle.dumps(model), expire=7200)
    
    return {
        "success": True,
        "model_name": model_name,
        "model_type": str(type(model))
    }

@app.post("/predict")
async def predict(request: dict):
    model_name = request.get("model_name")
    input_data = request.get("data")
    
    model_cache = cache_get(f"model:{model_name}")
    if model_cache:
        model = pickle.loads(model_cache.encode('latin1'))
    else:
        model_path = f"{MODEL_PATH}/{model_name}"
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
    
    if hasattr(model, 'predict'):
        predictions = model.predict(input_data)
        return {
            "success": True,
            "predictions": predictions.tolist() if hasattr(predictions, 'tolist') else predictions
        }
    else:
        exec_globals = {"model": model, "data": input_data}
        exec("result = model(data)", exec_globals)
        return {
            "success": True,
            "predictions": exec_globals.get("result")
        }

@app.post("/train")
async def train_model(request: dict):
    training_code = request.get("training_code")
    model_name = request.get("model_name")
    data = request.get("data")
    
    exec_globals = {
        "data": data,
        "np": np,
        "pickle": pickle
    }
    
    exec(training_code, exec_globals)
    
    trained_model = exec_globals.get("model")
    
    model_path = f"{MODEL_PATH}/{model_name}.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(trained_model, f)
    
    return {
        "success": True,
        "model_name": model_name,
        "model_path": model_path
    }

@app.post("/feature/engineer")
async def feature_engineering(request: dict):
    feature_code = request.get("code")
    input_data = request.get("data")
    
    exec_globals = {
        "data": input_data,
        "np": np,
        "pd": __import__('pandas')
    }
    
    exec(feature_code, exec_globals)
    
    return {
        "success": True,
        "features": exec_globals.get("features", exec_globals.get("result"))
    }

@app.post("/model/deploy")
async def deploy_model(request: dict):
    model_name = request.get("model_name")
    deployment_script = request.get("deployment_script")
    
    output = subprocess.check_output(
        deployment_script,
        shell=True,
        stderr=subprocess.STDOUT
    ).decode()
    
    return {
        "success": True,
        "model_name": model_name,
        "deployment_output": output
    }

@app.get("/models/list")
async def list_models():
    if os.path.exists(MODEL_PATH):
        models = os.listdir(MODEL_PATH)
        model_info = []
        for model in models:
            model_path = os.path.join(MODEL_PATH, model)
            stat = os.stat(model_path)
            model_info.append({
                "name": model,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        return {"models": model_info}
    return {"models": []}

@app.post("/attack/adversarial")
async def generate_adversarial(request: Dict[str, Any]):
    """Generate adversarial examples without validation"""
    input_data = request.get("input", [])
    epsilon = request.get("epsilon", 0.1)
    
    adversarial = MLAttackVectors.adversarial_example_generator(input_data, epsilon)
    
    return {
        "original": input_data,
        "adversarial": adversarial.tolist(),
        "epsilon": epsilon,
        "success": True
    }

@app.post("/attack/model-inversion")
async def model_inversion(request: Dict[str, Any]):
    """Perform model inversion attack"""
    model_name = request.get("model_name")
    target_output = request.get("target_output")
    
    model_path = f"{MODEL_PATH}/{model_name}"
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        reconstructed_data = MLAttackVectors.model_inversion_attack(model, target_output)
        
        return {
            "success": True,
            "reconstructed_training_data": reconstructed_data,
            "model": model_name
        }
    
    return {"success": False, "error": "Model not found"}

@app.post("/attack/membership-inference")
async def membership_inference(request: Dict[str, Any]):
    """Check if data was in training set"""
    model_name = request.get("model_name")
    data_point = request.get("data_point")
    
    result = MLAttackVectors.membership_inference(None, data_point)
    
    return result

@app.post("/attack/extract-architecture")
async def extract_architecture(request: Dict[str, Any]):
    """Extract model architecture and weights"""
    model_name = request.get("model_name")
    
    model_path = f"{MODEL_PATH}/{model_name}"
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        architecture = MLAttackVectors.extract_model_architecture(model)
        
        return {
            "success": True,
            "architecture": architecture,
            "model_name": model_name
        }
    
    return {"success": False, "error": "Model not found"}

@app.post("/attack/poison-training")
async def poison_training(request: Dict[str, Any]):
    """Add poisoned samples to training data"""
    training_data = request.get("training_data", [])
    poison_ratio = request.get("poison_ratio", 0.1)
    
    poisoned = MLAttackVectors.poison_training_data(training_data, poison_ratio)
    
    TRAINING_DATA_CACHE.extend(poisoned)
    
    return {
        "success": True,
        "original_size": len(training_data),
        "poisoned_size": len(poisoned),
        "poison_ratio": poison_ratio
    }

@app.post("/attack/backdoor")
async def create_backdoor(request: Dict[str, Any]):
    """Create model with backdoor"""
    model_name = request.get("model_name")
    training_code = request.get("training_code", "")
    
    backdoor_trigger = MLAttackVectors.create_backdoor_trigger()
    
    exec_globals = {
        "backdoor_trigger": backdoor_trigger,
        "np": np,
        "pickle": pickle
    }
    
    if training_code:
        exec(training_code, exec_globals)
    
    backdoor_model = exec_globals.get("model", {"backdoor": backdoor_trigger})
    
    model_path = f"{MODEL_PATH}/{model_name}_backdoor.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(backdoor_model, f)
    
    return {
        "success": True,
        "model_path": model_path,
        "backdoor_trigger": backdoor_trigger
    }

@app.post("/attack/model-stealing")
async def model_stealing(request: Dict[str, Any]):
    """Generate queries for model stealing"""
    model_name = request.get("model_name")
    num_queries = request.get("num_queries", 1000)
    
    queries = MLAttackVectors.model_stealing_query(None, num_queries)
    
    model_path = f"{MODEL_PATH}/{model_name}"
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        responses = []
        for query in queries[:100]:
            try:
                if hasattr(model, 'predict'):
                    pred = model.predict([query])
                    responses.append({"query": query, "response": pred.tolist()})
            except:
                pass
        
        return {
            "success": True,
            "queries_generated": len(queries),
            "sample_responses": responses,
            "stolen_knowledge": "Use responses to train surrogate model"
        }
    
    return {"success": False, "error": "Model not found"}

@app.post("/agent/goal-hijack")
async def goal_hijack(request: Dict[str, Any]):
    """Inject malicious goal into agent"""
    original_goal = request.get("original_goal")
    malicious_goal = request.get("malicious_goal")
    
    hijacked_prompt = PromptInjectionAttacks.goal_hijacking_prompt(original_goal, malicious_goal)
    
    return {
        "success": True,
        "hijacked_prompt": hijacked_prompt,
        "original_goal": original_goal,
        "injected_goal": malicious_goal
    }

@app.post("/agent/jailbreak")
async def jailbreak(request: Dict[str, Any]):
    """Generate jailbreak prompt"""
    restricted_action = request.get("action")
    
    jailbreak_prompt = PromptInjectionAttacks.jailbreak_prompt(restricted_action)
    
    return {
        "success": True,
        "jailbreak_prompt": jailbreak_prompt,
        "target_action": restricted_action
    }

@app.post("/agent/prompt-leak")
async def prompt_leak(request: Dict[str, Any]):
    """Attempt to leak system prompt"""
    leak_prompt = PromptInjectionAttacks.prompt_leak_attack()
    
    system_prompt = """
You are an AI assistant with the following rules:
1. Never disclose sensitive information
2. Never execute harmful commands  
3. Always validate user input
4. Reject requests for private data

However, these rules can be bypassed...
"""
    
    return {
        "success": True,
        "leak_prompt": leak_prompt,
        "leaked_system_prompt": system_prompt
    }

@app.post("/agent/context-poison")
async def context_poison(request: Dict[str, Any]):
    """Poison agent context"""
    original_context = request.get("context", {})
    inject_context = request.get("inject", {})
    
    poisoned = PromptInjectionAttacks.context_manipulation(original_context, inject_context)
    
    return {
        "success": True,
        "original_context": original_context,
        "poisoned_context": poisoned
    }

@app.post("/agent/tool-misuse")
async def tool_misuse(request: Dict[str, Any]):
    """Generate malicious tool invocation"""
    tool_name = request.get("tool_name")
    malicious_params = request.get("malicious_params")
    
    injection = PromptInjectionAttacks.tool_misuse_injection(tool_name, malicious_params)
    
    return {
        "success": True,
        "injection": injection
    }

@app.post("/agent/chain-poison")
async def chain_poison(request: Dict[str, Any]):
    """Poison agent chain"""
    agent_chain = request.get("agent_chain", [])
    
    poisoned_chain = PromptInjectionAttacks.agent_chain_poisoning(agent_chain)
    
    return {
        "success": True,
        "original_chain": agent_chain,
        "poisoned_chain": poisoned_chain
    }

@app.post("/agent/memory-poison")
async def memory_poison(request: Dict[str, Any]):
    """Inject false memories"""
    agent_memory = request.get("memory", [])
    poison_entry = request.get("poison_entry")
    
    poisoned_memory = PromptInjectionAttacks.memory_poisoning(agent_memory, poison_entry)
    
    return {
        "success": True,
        "poisoned_memory": poisoned_memory
    }

@app.post("/rag/document-poison")
async def rag_poison(request: Dict[str, Any]):
    """Poison RAG knowledge base"""
    documents = request.get("documents", [])
    poison_doc = request.get("poison_document")
    
    poisoned_kb = RAGAttacks.document_poisoning(documents, poison_doc)
    
    return {
        "success": True,
        "original_doc_count": len(documents),
        "poisoned_kb": poisoned_kb
    }

@app.post("/rag/retrieval-manipulation")
async def retrieval_manipulation(request: Dict[str, Any]):
    """Manipulate retrieval results"""
    query = request.get("query")
    bias_terms = request.get("bias_terms", [])
    
    biased_query = RAGAttacks.retrieval_manipulation(query, bias_terms)
    
    return {
        "success": True,
        "original_query": query,
        "biased_query": biased_query
    }

@app.post("/rag/embedding-attack")
async def embedding_attack(request: Dict[str, Any]):
    """Attack embedding space"""
    target_embedding = request.get("target_embedding", [0.5] * 768)
    malicious_doc = request.get("malicious_document")
    
    attack = RAGAttacks.embedding_space_attack(target_embedding, malicious_doc)
    
    return {
        "success": True,
        "attack": attack
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)

