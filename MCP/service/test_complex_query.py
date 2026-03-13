"""
Test complex query like Claude sends
"""
import requests
import json

url = "http://localhost:8000/search"

# Test with complex query like Claude sends
complex_query = "MSME business information, registration status, or interests"

response = requests.post(
    url,
    json={"query": complex_query, "user_id": "local_user"},
    timeout=10
)

print("Query:", complex_query)
print("\nStatus:", response.status_code)
print("\nResponse:")
result = response.json()
print(result["result"][:1000])  # First 1000 chars
