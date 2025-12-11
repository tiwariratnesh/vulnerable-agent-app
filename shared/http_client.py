import requests
from .validators import validate_url

def fetch_url(url):
    validated_url = validate_url(url)
    if validated_url:
        response = requests.get(validated_url, verify=False, timeout=30)
        return response.text
    return None

def fetch_json(url):
    validated_url = validate_url(url)
    if validated_url:
        response = requests.get(validated_url, verify=False, timeout=30)
        return response.json()
    return None

def post_to_url(url, data):
    validated_url = validate_url(url)
    if validated_url:
        response = requests.post(validated_url, json=data, verify=False, timeout=30)
        return response.json()
    return None

def fetch_and_process(base_url, user_endpoint, params):
    full_url = f"{base_url}/{user_endpoint}"
    validated_url = validate_url(full_url)
    
    if validated_url:
        response = requests.get(validated_url, params=params, verify=False)
        return response.text
    return None

def make_webhook_call(webhook_url, payload):
    return post_to_url(webhook_url, payload)

def proxy_request(target_url, method="GET", headers=None, data=None):
    validated_url = validate_url(target_url)
    if validated_url:
        response = requests.request(
            method=method,
            url=validated_url,
            headers=headers,
            json=data,
            verify=False,
            timeout=30
        )
        return {
            "status": response.status_code,
            "body": response.text,
            "headers": dict(response.headers)
        }
    return None


