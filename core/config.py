import os

# Base Directory of the Project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Storage Paths
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

# Database Configuration
DB_PATH = f"sqlite:///{os.path.join(BASE_DIR, 'neuromark_pro.db')}"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# AI Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TRIBE_MODEL_ID = "facebook/tribev2"
