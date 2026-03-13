from google import genai
import config
import json

class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.default_model = 'gemini-2.0-flash-exp'
    
    def generate_text(self, prompt, temperature=0.7, model=None):
        """Generate text response from Gemini"""
        try:
            response = self.client.models.generate_content(
                model=model or self.default_model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def generate_json(self, prompt, temperature=0.3, model=None):
        """Generate JSON response from Gemini"""
        try:
            full_prompt = f"{prompt}\n\nRespond with valid JSON only, no markdown formatting."
            
            response = self.client.models.generate_content(
                model=model or self.default_model,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    response_mime_type="application/json"
                )
            )
            
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
                text = text.strip()
            
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}\nResponse: {text}")
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
