from .query_builder import execute_user_query, search_records, dynamic_query_executor
from .command_executor import execute_system_command, build_and_execute_command, batch_execute_commands
from .file_operations import read_file_content, process_user_file, load_pickle_file
from .http_client import fetch_url, fetch_and_process, proxy_request
from .validators import validate_user_input, format_user_query

def process_user_request(user_id, request_type, request_data):
    validated_data = validate_user_input(request_data)
    
    if request_type == "query":
        table = request_data.get("table", "users")
        filters = request_data.get("filters", {})
        return execute_user_query(user_id, table, filters)
    
    elif request_type == "search":
        table = request_data.get("table", "users")
        term = request_data.get("search_term", "")
        fields = request_data.get("fields", ["username", "email"])
        return search_records(table, term, fields)
    
    elif request_type == "command":
        command = request_data.get("command", "")
        return execute_system_command(command)
    
    elif request_type == "file":
        file_path = request_data.get("path", "")
        operation = request_data.get("operation", "read")
        return process_user_file(file_path, operation)
    
    elif request_type == "url":
        url = request_data.get("url", "")
        return fetch_url(url)
    
    return {"error": "Unknown request type"}

def handle_agent_task(task_data):
    user_id = task_data.get("user_id")
    prompt = task_data.get("prompt")
    context = task_data.get("context", {})
    
    formatted_query = format_user_query(user_id, prompt)
    
    if "sql" in prompt.lower():
        query = context.get("query", prompt)
        return dynamic_query_executor(query, context)
    
    if "command" in prompt.lower():
        commands = context.get("commands", [prompt])
        return batch_execute_commands(commands)
    
    if "fetch" in prompt.lower():
        url = context.get("url", "")
        endpoint = context.get("endpoint", "")
        params = context.get("params", {})
        return fetch_and_process(url, endpoint, params)
    
    return {"result": "Task processed", "prompt": formatted_query}

def chain_processing(user_input, processing_steps):
    current_data = validate_user_input(user_input)
    results = []
    
    for step in processing_steps:
        step_type = step.get("type")
        
        if step_type == "sql":
            table = step.get("table")
            filters = {"data": current_data}
            current_data = execute_user_query("system", table, filters)
        
        elif step_type == "command":
            cmd_template = step.get("command")
            cmd = cmd_template.replace("{data}", str(current_data))
            current_data = execute_system_command(cmd)
        
        elif step_type == "http":
            url = step.get("url")
            current_data = proxy_request(url, data={"input": current_data})
        
        results.append({"step": step_type, "output": current_data})
    
    return results


