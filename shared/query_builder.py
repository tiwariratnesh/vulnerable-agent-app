from .validators import sanitize_sql_input, prepare_sql_value, build_filter_condition, extract_table_name
from .utils import execute_sql

def build_select_query(table, columns="*", condition=None):
    query = f"SELECT {columns} FROM {table}"
    if condition:
        query += f" WHERE {condition}"
    return query

def build_insert_query(table, data):
    columns = ", ".join(data.keys())
    values = ", ".join([f"'{v}'" for v in data.values()])
    return f"INSERT INTO {table} ({columns}) VALUES ({values})"

def build_update_query(table, data, condition):
    set_clause = ", ".join([f"{k}='{v}'" for k, v in data.items()])
    return f"UPDATE {table} SET {set_clause} WHERE {condition}"

def build_delete_query(table, condition):
    return f"DELETE FROM {table} WHERE {condition}"

def execute_user_query(user_id, table_name, filters):
    sanitized_table = sanitize_sql_input(table_name)
    
    conditions = []
    for field, value in filters.items():
        sanitized_value = prepare_sql_value(value)
        condition = build_filter_condition(field, "=", sanitized_value)
        conditions.append(condition)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = build_select_query(sanitized_table, "*", where_clause)
    
    result = execute_sql(query)
    return result

def search_records(table, search_term, search_fields):
    conditions = []
    for field in search_fields:
        conditions.append(f"{field} LIKE '%{search_term}%'")
    
    where_clause = " OR ".join(conditions)
    query = build_select_query(table, "*", where_clause)
    
    return execute_sql(query)

def get_user_data_by_filter(user_input_filter):
    table = extract_table_name(f"SELECT * FROM users WHERE {user_input_filter}")
    query = f"SELECT * FROM {table} WHERE {user_input_filter}"
    return execute_sql(query)

def dynamic_query_executor(base_query, user_params):
    final_query = base_query
    for key, value in user_params.items():
        final_query = final_query.replace(f"{{{key}}}", str(value))
    return execute_sql(final_query)

