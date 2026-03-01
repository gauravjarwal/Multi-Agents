"""
config.py
─────────
Central configuration — loads API keys from .env and provides defaults.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # reads .env in the same directory (or parent)

# ── API keys ──────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Server settings ──────────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True
