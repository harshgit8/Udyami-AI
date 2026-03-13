import os
from groq import Groq
import json
import config

client = Groq(api_key=os.environ.get("GROQ_API_KEY") or config.GROQ_API_KEY)

class GroqClient:
    def __init__(self, model_name='llama-3.3-70b-versatile'):
        self.model_name = model_name
    
    def generate(self, prompt, temperature=0.1):
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=8192
        )
        return response.choices[0].message.content
    
    def generate_json(self, prompt, temperature=0.1):
        response_text = self.generate(prompt, temperature)
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response_text[start:end])
            return json.loads(response_text)
        except json.JSONDecodeError:
            raise Exception(f"Failed to parse JSON from response: {response_text}")