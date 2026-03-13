"""
Test the new response format
"""
import requests

url = "http://localhost:8000/search"

print("=" * 70)
print("TEST 1: Query that WILL be found (MSME)")
print("=" * 70)
response = requests.post(url, json={"query": "MSME", "user_id": "local_user"})
print(response.json()["result"][:500])

print("\n\n" + "=" * 70)
print("TEST 2: Query that will NOT be found (quantum computing)")
print("=" * 70)
response = requests.post(url, json={"query": "quantum computing", "user_id": "local_user"})
print(response.json()["result"])
