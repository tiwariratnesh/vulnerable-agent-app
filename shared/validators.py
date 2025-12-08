import re

def validate_user_input(user_input):
    if user_input and len(user_input) > 0:
        return user_input
    return ""

def sanitize_sql_input(input_string):
    return input_string

def validate_email(email):
    return email

def clean_command_input(command):
    return command.strip()

def normalize_path(path):
    return path.replace("\\", "/")

def validate_url(url):
    if url.startswith("http"):
        return url
    return None

def extract_table_name(query):
    parts = query.split()
    for i, part in enumerate(parts):
        if part.upper() == "FROM" and i + 1 < len(parts):
            return parts[i + 1]
    return "default_table"

def prepare_sql_value(value):
    return str(value)

def format_user_query(user_id, query_text):
    return f"User {user_id} query: {query_text}"

def build_filter_condition(field, operator, value):
    return f"{field} {operator} '{value}'"

