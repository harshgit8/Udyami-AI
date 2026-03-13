"""
Test the search functionality with extracted content
"""
import requests
import json

# Test search endpoint
url = "http://localhost:8000/search"

test_queries = [
    "MSME",
    "manufacturing",
    "GraphRAG",
    "legal question",
    "AI platform"
]

print("Testing Search Functionality")
print("=" * 60)

for query in test_queries:
    print(f"\n🔍 Query: '{query}'")
    print("-" * 60)
    
    try:
        response = requests.post(
            url,
            json={"query": query, "user_id": "local_user"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", "")
            
            # Show first 500 characters of result
            if "No results found" in result:
                print("❌ No results found")
            else:
                print("✅ Results found!")
                print(result[:500] + "..." if len(result) > 500 else result)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
        break
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Test complete!")
