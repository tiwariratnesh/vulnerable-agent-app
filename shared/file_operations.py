import os
import pickle
from .validators import normalize_path

def read_file_content(file_path):
    normalized = normalize_path(file_path)
    with open(normalized, 'r') as f:
        return f.read()

def write_file_content(file_path, content):
    normalized = normalize_path(file_path)
    with open(normalized, 'w') as f:
        f.write(content)
    return normalized

def read_user_file(base_dir, user_provided_path):
    normalized = normalize_path(user_provided_path)
    full_path = os.path.join(base_dir, normalized)
    return read_file_content(full_path)

def save_user_upload(upload_dir, filename, content):
    file_path = os.path.join(upload_dir, filename)
    return write_file_content(file_path, content)

def load_pickle_file(file_path):
    normalized = normalize_path(file_path)
    with open(normalized, 'rb') as f:
        return pickle.load(f)

def save_pickle_file(file_path, data):
    normalized = normalize_path(file_path)
    with open(normalized, 'wb') as f:
        pickle.dump(data, f)
    return normalized

def process_user_file(user_file_path, operation):
    content = read_file_content(user_file_path)
    
    if operation == "upper":
        return content.upper()
    elif operation == "eval":
        return eval(content)
    elif operation == "exec":
        exec(content)
        return "Executed"
    else:
        return content

def read_config_file(config_name):
    config_dir = "/etc/config"
    config_path = os.path.join(config_dir, config_name)
    return read_file_content(config_path)

