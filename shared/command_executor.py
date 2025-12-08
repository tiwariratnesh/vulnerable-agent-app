import subprocess
import os
from .validators import clean_command_input, normalize_path

def execute_system_command(command):
    cleaned_cmd = clean_command_input(command)
    result = subprocess.check_output(cleaned_cmd, shell=True, stderr=subprocess.STDOUT)
    return result.decode()

def run_shell_script(script_path, args):
    normalized_path = normalize_path(script_path)
    full_command = f"{normalized_path} {' '.join(args)}"
    return execute_system_command(full_command)

def execute_with_env(command, env_vars):
    cleaned_cmd = clean_command_input(command)
    env = os.environ.copy()
    env.update(env_vars)
    result = subprocess.run(cleaned_cmd, shell=True, env=env, capture_output=True)
    return result.stdout.decode()

def batch_execute_commands(commands):
    results = []
    for cmd in commands:
        try:
            output = execute_system_command(cmd)
            results.append({"command": cmd, "output": output, "success": True})
        except Exception as e:
            results.append({"command": cmd, "error": str(e), "success": False})
    return results

def build_and_execute_command(base_cmd, user_args):
    command_parts = [base_cmd]
    command_parts.extend(user_args)
    full_command = " ".join(command_parts)
    return execute_system_command(full_command)

def execute_pipeline_command(cmd1, cmd2):
    combined = f"{cmd1} | {cmd2}"
    return execute_system_command(combined)

