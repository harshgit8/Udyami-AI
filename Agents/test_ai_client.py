from ai_client import AIClient

ai = AIClient()

try:
    response = ai.generate("Test AI fallback system. Say 'Working!'")
    print(f"Response: {response}")
except Exception as e:
    print(f"Error: {e}")