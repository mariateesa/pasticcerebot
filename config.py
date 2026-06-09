import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OLLAMA_MODEL = "llama3.2:1b"
OLLAMA_BASE_URL = "http://localhost:11434"
RICETTE_DIR = os.path.join(os.path.dirname(__file__), "data", "ricette")
CHUNK_SIZE = 400
TOP_K = 3
