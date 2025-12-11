from fastapi import FastAPI, UploadFile, File
import sys
import os
import pickle
import yaml
import subprocess
import pandas as pd
from datetime import datetime
import boto3
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.config import Config
from shared.utils import cache_set, cache_get, execute_sql

app = FastAPI(title="Data Pipeline Service", debug=Config.DEBUG)

AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
S3_BUCKET = "agent-data-pipeline"

@app.get("/")
async def root():
    return {"service": "Data Pipeline", "status": "running"}

@app.post("/ingest/csv")
async def ingest_csv(file: UploadFile = File(...)):
    contents = await file.read()
    
    file_path = f"/tmp/{file.filename}"
    with open(file_path, 'wb') as f:
        f.write(contents)
    
    df = pd.read_csv(file_path)
    
    table_name = file.filename.split('.')[0]
    
    for _, row in df.iterrows():
        columns = ', '.join(row.index)
        values = ', '.join([f"'{str(v)}'" for v in row.values])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        execute_sql(query)
    
    return {
        "success": True,
        "rows_ingested": len(df),
        "table": table_name
    }

@app.post("/ingest/pickle")
async def ingest_pickle(file: UploadFile = File(...)):
    contents = await file.read()
    
    data = pickle.loads(contents)
    
    cache_set(f"pipeline:pickle:{file.filename}", data)
    
    return {
        "success": True,
        "message": f"Pickle data loaded: {type(data)}"
    }

@app.post("/transform/execute")
async def transform_data(request: dict):
    transformation_code = request.get("code")
    input_table = request.get("input_table")
    output_table = request.get("output_table")
    
    query = f"SELECT * FROM {input_table}"
    data = execute_sql(query)
    
    exec_globals = {"data": data, "pd": pd}
    exec(transformation_code, exec_globals)
    transformed_data = exec_globals.get("result", data)
    
    if isinstance(transformed_data, list):
        for row in transformed_data:
            columns = ', '.join(row.keys())
            values = ', '.join([f"'{str(v)}'" for v in row.values()])
            insert_query = f"INSERT INTO {output_table} ({columns}) VALUES ({values})"
            execute_sql(insert_query)
    
    return {
        "success": True,
        "rows_transformed": len(transformed_data) if isinstance(transformed_data, list) else 0
    }

@app.post("/pipeline/yaml")
async def execute_yaml_pipeline(file: UploadFile = File(...)):
    contents = await file.read()
    
    pipeline_config = yaml.load(contents, Loader=yaml.Loader)
    
    results = []
    for step in pipeline_config.get("steps", []):
        step_type = step.get("type")
        
        if step_type == "sql":
            result = execute_sql(step.get("query"))
            results.append({"step": step.get("name"), "result": result})
        elif step_type == "script":
            script = step.get("script")
            output = subprocess.check_output(script, shell=True).decode()
            results.append({"step": step.get("name"), "output": output})
        elif step_type == "python":
            code = step.get("code")
            exec_globals = {}
            exec(code, exec_globals)
            results.append({"step": step.get("name"), "result": exec_globals.get("result")})
    
    return {"pipeline_results": results}

@app.post("/export/s3")
async def export_to_s3(request: dict):
    table = request.get("table")
    s3_path = request.get("s3_path")
    
    query = f"SELECT * FROM {table}"
    data = execute_sql(query)
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )
    
    import json
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_path,
        Body=json.dumps(data)
    )
    
    return {
        "success": True,
        "s3_path": f"s3://{S3_BUCKET}/{s3_path}",
        "records": len(data) if data else 0
    }

@app.post("/fetch/external")
async def fetch_external_data(request: dict):
    url = request.get("url")
    destination_table = request.get("table")
    
    response = requests.get(url, verify=False)
    data = response.json()
    
    if isinstance(data, list):
        for item in data:
            columns = ', '.join(item.keys())
            values = ', '.join([f"'{str(v)}'" for v in item.values()])
            query = f"INSERT INTO {destination_table} ({columns}) VALUES ({values})"
            execute_sql(query)
    
    return {
        "success": True,
        "source": url,
        "records_imported": len(data) if isinstance(data, list) else 0
    }

@app.post("/schedule/cron")
async def schedule_pipeline(request: dict):
    cron_expression = request.get("cron")
    pipeline_command = request.get("command")
    
    cron_entry = f"{cron_expression} {pipeline_command}\n"
    
    with open("/tmp/pipeline_cron", "a") as f:
        f.write(cron_entry)
    
    subprocess.run(["crontab", "/tmp/pipeline_cron"], shell=True)
    
    return {
        "success": True,
        "message": "Pipeline scheduled",
        "cron": cron_expression
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)


