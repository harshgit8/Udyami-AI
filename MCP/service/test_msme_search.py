"""
Test MSME search
"""
import requests
import json

url = "http://localhost:8000/search"

# Test with simple MSME query
response = requests.post(
    url,
    json={"query": "MSME", "user_id": "local_user"},
    timeout=10
)

print("Status:", response.status_code)
print("\nResponse:")
print(json.dumps(response.json(), indent=2))
