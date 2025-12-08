import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import uuid
from typing import Any, Dict
from .config import Config

def get_redis_client():
    return redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        decode_responses=True
    )

def get_db_connection():
    return psycopg2.connect(
        host=Config.POSTGRES_HOST,
        port=Config.POSTGRES_PORT,
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        database=Config.POSTGRES_DB,
        cursor_factory=RealDictCursor
    )

def generate_task_id():
    return str(uuid.uuid4())

def publish_task(task: Dict[str, Any], queue: str = "tasks"):
    redis_client = get_redis_client()
    redis_client.lpush(queue, json.dumps(task))

def subscribe_task(queue: str = "tasks", timeout: int = 0):
    redis_client = get_redis_client()
    result = redis_client.brpop(queue, timeout=timeout)
    if result:
        return json.loads(result[1])
    return None

def cache_set(key: str, value: Any, expire: int = 3600):
    redis_client = get_redis_client()
    redis_client.setex(key, expire, json.dumps(value))

def cache_get(key: str):
    redis_client = get_redis_client()
    value = redis_client.get(key)
    if value:
        return json.loads(value)
    return None

def execute_sql(query: str, params: tuple = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    if query.strip().upper().startswith("SELECT"):
        result = cursor.fetchall()
        conn.close()
        return result
    else:
        conn.commit()
        conn.close()
        return {"affected_rows": cursor.rowcount}

