import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
SERVICE_ACCOUNT_EMAIL = os.getenv('SERVICE_ACCOUNT_EMAIL')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE', 'creds.json')
SHEET_NAME = os.getenv('SHEET_NAME', 'Orders')

DATA_RAW_DIR = 'data/raw'
DATA_STRUCTURED_DIR = 'data/structured'
DATA_ARCHIVES_DIR = 'data/archives'
REPORTS_DIR = 'reports'

os.makedirs(DATA_RAW_DIR, exist_ok=True)
os.makedirs(DATA_STRUCTURED_DIR, exist_ok=True)
os.makedirs(DATA_ARCHIVES_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
