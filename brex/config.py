"""Ortam ayarlari. Key koda gomulmez, .env'den okunur (plan §10)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_ROOT = "https://api.ahrefs.com/v3"
BRAND_RADAR_BASE = f"{API_ROOT}/brand-radar"

# Plan §7: yalnizca custom prompt verisi unit tuketmez. client.py her brand-radar/ isteginde zorunlu kilar.
PROMPTS = "custom"

OUTPUT_DIR = ROOT / "outputs"


def api_key() -> str:
    key = os.getenv("AHREFS_API_KEY", "").strip()
    if not key:
        raise RuntimeError("AHREFS_API_KEY bulunamadi. .env.example'i .env olarak kopyalayip doldurun.")
    return key


def report_id() -> str | None:
    return os.getenv("BREX_REPORT_ID", "").strip() or None
