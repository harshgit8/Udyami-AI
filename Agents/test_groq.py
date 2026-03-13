import os
from groq import Groq

# Load from environment variable
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": "Hello, test Groq API connection. Respond with 'Groq API working!'"}],
        model="llama-3.3-70b-versatile"
    )
    print(f"✅ Groq Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Groq Error: {e}")