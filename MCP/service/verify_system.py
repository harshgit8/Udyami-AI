"""
Verify the complete system is working
"""
import requests
import json
from pathlib import Path

print("=" * 70)
print("UDYAMI AI SYSTEM VERIFICATION")
print("=" * 70)

# 1. Check backend health
print("\n1. Checking Backend Health...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Backend is running: {data}")
    else:
        print(f"   ❌ Backend returned status {response.status_code}")
except Exception as e:
    print(f"   ❌ Backend not responding: {e}")
    print("   → Start backend: python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000")

# 2. Check processed files
print("\n2. Checking Processed Files...")
processed_dir = Path("uploads/local_user/processed/docs")
if processed_dir.exists():
    meta_files = list(processed_dir.glob("*.meta"))
    print(f"   Found {len(meta_files)} processed documents:")
    
    for meta_file in meta_files:
        with open(meta_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            has_content = metadata.get('has_content', False)
            content_length = metadata.get('content_length', 0)
            status = "✅" if has_content else "❌"
            print(f"   {status} {metadata.get('old_name', meta_file.stem)}")
            print(f"      Content extracted: {has_content}, Length: {content_length} chars")
else:
    print("   ❌ No processed files directory found")

# 3. Test search
print("\n3. Testing Search Functionality...")
try:
    response = requests.post(
        "http://localhost:8000/search",
        json={"query": "polymer", "user_id": "local_user"},
        timeout=10
    )
    if response.status_code == 200:
        result = response.json()
        if "Found" in result['result']:
            print("   ✅ Search is working")
            print(f"   Query: 'polymer'")
            print(f"   {result['result'].split(chr(10))[0]}")  # First line
        else:
            print("   ⚠️  Search returned no results")
    else:
        print(f"   ❌ Search failed with status {response.status_code}")
except Exception as e:
    print(f"   ❌ Search test failed: {e}")

# 4. Check MCP server build
print("\n4. Checking MCP Server...")
mcp_dist = Path("../Udyami-mcp-docker/dist/index.js")
if mcp_dist.exists():
    print(f"   ✅ MCP server built: {mcp_dist}")
    # Check if it's the new version
    with open(mcp_dist, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'Udyami AI' in content:
            print("   ✅ MCP server has new name: 'Udyami AI'")
        else:
            print("   ⚠️  MCP server still has old name")
else:
    print("   ❌ MCP server not built")
    print("   → Run: cd Udyami-mcp-docker && npm run build")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("\nTo fix any issues:")
print("1. Restart backend: python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000")
print("2. Reprocess old files: python extract_documents.py")
print("3. Upload new files through frontend: http://localhost:3000/dashboard/upload")
print("4. Restart Claude Desktop to load updated MCP server")
print("\n" + "=" * 70)
