"""
MuzaffarZed AI Video Bot - Konfiguratsiya va Sozlamalar
Muallif: MuzaffarZed
"""
import os
from pathlib import Path

# Asosiy papkalar
BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"

for p in [TEMP_DIR, OUTPUT_DIR, ASSETS_DIR, MUSIC_DIR, FONTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# API Kalitlari (Atrof-muhitdan yoki to'g'ridan-to'g'ri)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")

# Ovozlar ro'yxati (Edge-TTS)
VOICES = {
    "uz_sardor": {
        "name": "Sardor (O'zbekcha Erkak)",
        "id": "uz-UZ-SardorNeural",
        "lang": "uz"
    },
    "uz_madina": {
        "name": "Madina (O'zbekcha Ayol)",
        "id": "uz-UZ-MadinaNeural",
        "lang": "uz"
    },
    "ru_dmitry": {
        "name": "Dmitriy (Ruscha Erkak)",
        "id": "ru-RU-DmitryNeural",
        "lang": "ru"
    },
    "ru_svetlana": {
        "name": "Svetlana (Ruscha Ayol)",
        "id": "ru-RU-SvetlanaNeural",
        "lang": "ru"
    },
    "en_christopher": {
        "name": "Christopher (Inglizcha Erkak)",
        "id": "en-US-ChristopherNeural",
        "lang": "en"
    },
    "en_aria": {
        "name": "Aria (Inglizcha Ayol)",
        "id": "en-US-AriaNeural",
        "lang": "en"
    }
}
DEFAULT_VOICE = "uz_sardor"

# Video parametrlari (Standart: Reels/Shorts 9:16)
FORMATS = {
    "9:16": {"width": 1080, "height": 1920, "name": "Reels / Shorts (9:16)"},
    "16:9": {"width": 1920, "height": 1080, "name": "YouTube (16:9)"},
    "1:1": {"width": 1080, "height": 1080, "name": "Post (1:1)"}
}
DEFAULT_FORMAT = "9:16"
FPS = 30

# Brend va Mualliflik imzosi (Qat'iy Oliy Qoida)
WATERMARK_TEXT = "Dasturchi: MuzaffarZed"
