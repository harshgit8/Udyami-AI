import time
import logging

from gemini_client import GeminiClient
from groq_client import GroqClient
import json

class AIClient:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.groq_client = GroqClient()
    
    def generate(self, prompt, temperature=0.1):
        try:
            response = self.gemini_client.generate(prompt, temperature)
            print("🟢 Gemini")
            return response
        except Exception:
            try:
                time.sleep(2)  # Rate limiting
                response = self.groq_client.generate(prompt, temperature)
                print("🟡 Groq")
                return response
            except Exception:
                print("🔴 Both APIs failed")
                raise Exception("All AI services failed")
    
    def generate_json(self, prompt, temperature=0.1):
        try:
            response = self.gemini_client.generate_json(prompt, temperature)
            print("🟢 Gemini JSON")
            return response
        except Exception:
            try:
                time.sleep(2)  # Rate limiting
                response = self.groq_client.generate_json(prompt, temperature)
                print("🟡 Groq JSON")
                return response
            except Exception:
                print("🔴 Both APIs failed")
                raise Exception("All AI services failed")