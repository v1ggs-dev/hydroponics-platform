import os
from pathlib import Path
from dotenv import load_dotenv

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

load_dotenv(ROOT_DIR / '.env')

# Vision (AI-1) config
MODEL_PATH = ROOT_DIR / 'models' / 'vision' / 'best_v1.pt'
CONFIDENCE_THRESHOLD = 0.25
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
MAX_FILE_SIZE = 10 * 1024 * 1024
API_VERSION = 'v1'
MODEL_VERSION = 'vision-v1'

# RAG (AI-4) config
KNOWLEDGE_DIR = ROOT_DIR / 'data' / 'knowledge'
FAISS_INDEX_DIR = ROOT_DIR / 'models' / 'rag'
EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

# Groq LLM config
GROQ_MODEL = 'llama-3.3-70b-versatile'
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# IoT Platform backend (teammate's Node.js backend)
IOT_BACKEND_URL = os.getenv('IOT_BACKEND_URL', 'http://localhost:4000/api/v1')
