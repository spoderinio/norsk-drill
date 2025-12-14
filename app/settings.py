"""Application settings."""
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/data/norsk_drill.db"

# Personal mode (no authentication required)
PERSONAL_MODE = True

# Admin access (only on localhost in personal mode)
ADMIN_LOCALHOST_ONLY = True
