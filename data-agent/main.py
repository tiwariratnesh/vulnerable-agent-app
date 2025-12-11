from fastapi import FastAPI
import sys
import os
from datetime import datetime
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import Config
from shared.utils import execute_sql, get_db_connection, cache_set, cache_get

app = FastAPI(title="Data Agent", debug=Config.DEBUG)

@app.get("/")
async def root():
    return {"service": "Data Agent", "status": "running"}

@app.post("/query")
async def query_data(request: dict):
    query_type = request.get("query_type")
    query = request.get("query")
    user_id = request.get("user_id")
    
    try:
        if query_type == "sql":
            result = execute_sql(query)
            return {
                "success": True,
                "data": result,
                "query": query,
                "user_id": user_id
            }
        elif query_type == "cache":
            cache_key = query
            cached_data = cache_get(cache_key)
            return {
                "success": True,
                "data": cached_data,
                "query": query
            }
        else:
            return {
                "success": False,
                "error": "Unsupported query type"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

@app.post("/user/profile")
async def get_user_profile(request: dict):
    user_id = request.get("user_id")
    
    query = f"SELECT * FROM users WHERE user_id = '{user_id}'"
    result = execute_sql(query)
    
    if result:
        return {"success": True, "profile": result[0] if result else None}
    return {"success": False, "error": "User not found"}

@app.post("/user/preferences")
async def update_preferences(request: dict):
    user_id = request.get("user_id")
    preferences = request.get("preferences", {})
    
    query = f"UPDATE users SET preferences = '{json.dumps(preferences)}' WHERE user_id = '{user_id}'"
    execute_sql(query)
    
    return {"success": True, "message": "Preferences updated"}

@app.post("/search")
async def search_data(request: dict):
    table = request.get("table")
    search_term = request.get("search_term")
    field = request.get("field", "*")
    
    query = f"SELECT {field} FROM {table} WHERE data LIKE '%{search_term}%'"
    result = execute_sql(query)
    
    return {
        "success": True,
        "results": result,
        "count": len(result) if result else 0
    }

@app.post("/export")
async def export_data(request: dict):
    table = request.get("table")
    condition = request.get("condition", "1=1")
    
    query = f"SELECT * FROM {table} WHERE {condition}"
    result = execute_sql(query)
    
    export_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_set(f"export:{export_id}", result, expire=7200)
    
    return {
        "success": True,
        "export_id": export_id,
        "records": len(result) if result else 0,
        "data": result
    }

@app.get("/admin/tables")
async def list_tables():
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    result = execute_sql(query)
    return {"tables": result}

@app.post("/admin/raw-query")
async def raw_query(request: dict):
    query = request.get("query")
    try:
        result = execute_sql(query)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)


