"""Environment settings. The API key is never hardcoded; it is read from .env (plan §10)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_ROOT = "https://api.ahrefs.com/v3"
BRAND_RADAR_BASE = f"{API_ROOT}/brand-radar"

# Plan §7: only custom prompt data is free of unit cost. client.py enforces this on every brand-radar/ request.
PROMPTS = "custom"

OUTPUT_DIR = ROOT / "outputs"


def api_key() -> str:
    key = os.getenv("AHREFS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("AHREFS_API_KEY not found. Copy .env.example to .env and fill it in.")
    return key


def report_id() -> str | None:
    return os.getenv("BREX_REPORT_ID", "").strip() or None
