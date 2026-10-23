"""
MuzaffarZed AI Video Bot - Konfiguratsiya va Sozlamalar (Ultimate Flagship 3.0)
Muallif: MuzaffarZed
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
SFX_DIR = ASSETS_DIR / "sfx"
FONTS_DIR = ASSETS_DIR / "fonts"

for p in [TEMP_DIR, OUTPUT_DIR, ASSETS_DIR, MUSIC_DIR, SFX_DIR, FONTS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")

# 1. Ovozlar ro'yxati (Edge-TTS)
VOICES = {
    "uz_sardor": {
        "name": "🇺🇿 Sardor (O'zbekcha Erkak)",
        "id": "uz-UZ-SardorNeural",
        "lang": "uz"
    },
    "uz_madina": {
        "name": "🇺🇿 Madina (O'zbekcha Ayol)",
        "id": "uz-UZ-MadinaNeural",
        "lang": "uz"
    },
    "ru_dmitry": {
        "name": "🇷🇺 Dmitriy (Ruscha Erkak)",
        "id": "ru-RU-DmitryNeural",
        "lang": "ru"
    },
    "ru_svetlana": {
        "name": "🇷🇺 Svetlana (Ruscha Ayol)",
        "id": "ru-RU-SvetlanaNeural",
        "lang": "ru"
    },
    "en_christopher": {
        "name": "🇺🇸 Christopher (Inglizcha Erkak)",
        "id": "en-US-ChristopherNeural",
        "lang": "en"
    },
    "en_aria": {
        "name": "🇺🇸 Aria (Inglizcha Ayol)",
        "id": "en-US-AriaNeural",
        "lang": "en"
    }
}
DEFAULT_VOICE = "uz_sardor"

# 2. Ovoz Rejimlari va Tonalitesi
VOICE_MODES = {
    "reels_fast": {
        "name": "🚀 Reels Dinamik (+12% tezlik, baquvvat)",
        "rate": "+12%",
        "pitch": "-1Hz"
    },
    "cinematic_deep": {
        "name": "🎬 Kinematik Chuqur (-3Hz bas)",
        "rate": "+5%",
        "pitch": "-3Hz"
    },
    "natural_clean": {
        "name": "🎙 Standart Tabiiy (1.0x me'yorda)",
        "rate": "+0%",
        "pitch": "+0Hz"
    },
    "energetic": {
        "name": "⚡ Energetik / TikTok (+16% tezyurar)",
        "rate": "+16%",
        "pitch": "+1Hz"
    }
}
DEFAULT_VOICE_MODE = "reels_fast"

# 3. Video Uslublari (Video Styles / Retention Formats)
VIDEO_STYLES = {
    "top_facts": {
        "name": "🔥 Top 3 Fakt (Shok va qiziqarli)",
        "desc": "3 ta hayratlanarli fakt ketma-ketligi"
    },
    "story": {
        "name": "💡 Chuqur Hikoya (Storytelling)",
        "desc": "Dramatik kirish, sir va hayotiy xulosa"
    },
    "motivation": {
        "name": "⚡ Kuchli Motivatsiya (Mindset)",
        "desc": "Qat'iyat, intizom va g'alaba energiyasi"
    },
    "science": {
        "name": "🌌 Ilmiy & Koinot Tadqiqoti",
        "desc": "Koinot, kashfiyotlar va buyuk sirlar"
    },
    "business": {
        "name": "💰 Biznes & Boylik Qoidalari",
        "desc": "Muvaffaqiyat, moliya va intellekt"
    }
}
DEFAULT_VIDEO_STYLE = "top_facts"

# 4. Subtitr Dizaynlari (Subtitle Color Schemes)
SUBTITLE_THEMES = {
    "gold": {
        "name": "🌟 Alex Hormozi Oltin",
        "active_color": "&H0000D7FF",   # BGR format for ASS (Gold Yellow)
        "base_color": "&H00FFFFFF",
        "outline_color": "&H00000000"
    },
    "emerald": {
        "name": "🟢 Neon Zumrad Kiber",
        "active_color": "&H007FFF00",   # Neon Emerald
        "base_color": "&H00FFFFFF",
        "outline_color": "&H00000000"
    },
    "fire": {
        "name": "🔴 Olovli Qizil (Action)",
        "active_color": "&H002020FF",   # Bright Fire Red
        "base_color": "&H00FFFFFF",
        "outline_color": "&H00000000"
    },
    "cyan": {
        "name": "🔵 Elektr Moviy (Cyan)",
        "active_color": "&H00FFFF00",   # Electric Cyan
        "base_color": "&H00FFFFFF",
        "outline_color": "&H00000000"
    }
}
DEFAULT_SUBTITLE_THEME = "gold"

# 5. Fon Musiqasi Janrlari
MUSIC_GENRES = {
    "auto": "✨ Mavzuga mos avtomatik",
    "ambient_chill": "🌌 Koinot / Tinch Ambient",
    "cosmic_deep": "🪐 Chuqur Sirli / Kosmik Bas",
    "epic_inspiration": "🔥 Epik Motivatsiya / Ilhom",
    "tech_modern": "🤖 Zamonaviy Kiber / Lo-Fi"
}
DEFAULT_MUSIC_GENRE = "auto"

# 6. Video Formati va Xavfsiz Zona
FORMATS = {
    "9:16": {"width": 1080, "height": 1920, "name": "Reels / Shorts (9:16)"},
    "16:9": {"width": 1920, "height": 1080, "name": "YouTube (16:9)"},
    "1:1": {"width": 1080, "height": 1080, "name": "Post (1:1)"}
}
DEFAULT_FORMAT = "9:16"
FPS = 30

# Instagram / TikTok xavfsiz zonasi (Safe Margin)
SUBTITLE_SAFE_MARGIN_V = 480

WATERMARK_TEXT = "Dasturchi: MuzaffarZed"
