import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Ollama Settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    MODEL_RAG = "qwen2.5:3b"
    MODEL_JUDGE = "qwen2.5-coder:3b"
    MODEL_GUARD = "llama-guard3:1b"
    
    # RAG Settings
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    TOP_K = 3
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    DOCS_DIR = os.path.join(DATA_DIR, "docs")
    OUTPUTS_DIR = os.path.join(DATA_DIR, "outputs")
    CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")
    
    # Guardrail Settings
    ENABLE_INPUT_GUARDS = os.getenv("ENABLE_INPUT_GUARDS", "true").lower() == "true"
    ENABLE_OUTPUT_GUARDS = os.getenv("ENABLE_OUTPUT_GUARDS", "true").lower() == "true"
    ALLOWED_TOPICS = ["finance", "technology", "artificial intelligence", "data science"]
    
    # Evaluation Thresholds
    MIN_FAITHFULNESS = float(os.getenv("MIN_FAITHFULNESS", "0.80"))
    MIN_ANSWER_RELEVANCY = float(os.getenv("MIN_ANSWER_RELEVANCY", "0.80"))
    
    # Mock Mode (Fallback if Ollama is down)
    MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

config = Config()

# Ensure directories exist
os.makedirs(config.DOCS_DIR, exist_ok=True)
os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
os.makedirs(os.path.join(config.BASE_DIR, "phase-b", "charts"), exist_ok=True)
