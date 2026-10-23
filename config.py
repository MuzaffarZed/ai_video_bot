"""
MuzaffarZed AI Video Bot - Konfiguratsiya va Sozlamalar (Quantum 9.0 Apex Supreme)
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
USER_UPLOADS_DIR = BASE_DIR / "user_uploads"

for p in [TEMP_DIR, OUTPUT_DIR, ASSETS_DIR, MUSIC_DIR, SFX_DIR, FONTS_DIR, USER_UPLOADS_DIR]:
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

# 3. Video Uslublari (Video Styles)
VIDEO_STYLES = {
    "top_facts": {
        "name": "🔥 Top Faktlar (Shok faktlar)",
        "desc": "Qiziqarli va shok qiluvchi faktlar ketma-ketligi"
    },
    "story": {
        "name": "💡 Chuqur Hikoya (Storytelling)",
        "desc": "Dramatik kirish, kulminatsiya va ibratli xulosa"
    },
    "motivation": {
        "name": "⚡ Kuchli Motivatsiya (Mindset)",
        "desc": "Qat'iyat, intizom va g'alaba energiyasi"
    },
    "science": {
        "name": "🌌 Ilmiy & Koinot Tadqiqoti",
        "desc": "Koinot, kvant fizikasi va buyuk sirlar"
    },
    "business": {
        "name": "💰 Biznes & Boylik Qoidalari",
        "desc": "Muvaffaqiyat, moliya va sarmoya sirlari"
    },
    "podcast_dialogue": {
        "name": "🎙 Ikki Kishilik Podkast (Sardor & Madina)",
        "desc": "Savol-javob va qizg'in bahs shaklidagi dinamik suhbat"
    }
}
DEFAULT_VIDEO_STYLE = "top_facts"

# 4. Kinematografik Rang Filtrlari (Visual LUTs / Color Grading)
VISUAL_FILTERS = {
    "teal_orange": {
        "name": "🎬 Kinematik Teal & Orange (Gollivud)",
        "filter": "eq=contrast=1.08:saturation=1.2:gamma_r=0.92:gamma_b=1.12"
    },
    "cyberpunk": {
        "name": "🌆 Kiberpank Neon (To'yingan yorug'lik)",
        "filter": "eq=contrast=1.14:saturation=1.35,colorchannelmixer=rr=1.05:bb=1.2:gg=0.95"
    },
    "golden": {
        "name": "🌟 Oltin Quyoshli (Golden Hour)",
        "filter": "eq=contrast=1.06:saturation=1.16,colorbalance=rs=0.08:gs=0.04:bs=-0.06"
    },
    "clean": {
        "name": "💎 Tiniq Zamonaviy (Clean HDR)",
        "filter": "eq=contrast=1.06:saturation=1.14"
    }
}
DEFAULT_VISUAL_FILTER = "teal_orange"

# 5. Subtitr O'lchamlari
SUBTITLE_SIZES = {
    "large": {"name": "🔠 Katta Pop (82px - Reels)", "size": 82},
    "medium": {"name": "🔡 Standart (74px)", "size": 74},
    "small": {"name": "🔤 Ixcham (64px - YouTube)", "size": 64}
}
DEFAULT_SUBTITLE_SIZE = "medium"

# 6. Davomiylik va Kadrlar Miqdori
DURATIONS = {
    "short_15": {
        "name": "⚡ Qisqa Tezkor (3 kadr ~18s)",
        "scene_count": 3
    },
    "medium_30": {
        "name": "🎬 Standart Reels (5 kadr ~30s)",
        "scene_count": 5
    },
    "deep_45": {
        "name": "💎 Chuqur Mini-Doku (7 kadr ~45s)",
        "scene_count": 7
    }
}
DEFAULT_DURATION = "short_15"

# 7. Video Formatlari
FORMATS = {
    "9:16": {
        "width": 1080,
        "height": 1920,
        "name": "📱 Vertikal Reels / Shorts (9:16)",
        "safe_margin_v": 480
    },
    "16:9": {
        "width": 1920,
        "height": 1080,
        "name": "🖥 Gorizontal YouTube (16:9)",
        "safe_margin_v": 120
    },
    "1:1": {
        "width": 1080,
        "height": 1080,
        "name": "⏹ Kvadrat Post / TG (1:1)",
        "safe_margin_v": 160
    }
}
DEFAULT_FORMAT = "9:16"
FPS = 30

# 8. Subtitr Rang Dizaynlari
SUBTITLE_THEMES = {
    "gold": {
        "name": "🌟 Alex Hormozi Oltin",
        "active_color": "&H0000D7FF",
        "base_color": "&H00FFFFFF",
        "outline_color": "&H00000000"
    },
    "emerald": {
        "name": "🟢 Neon Zumrad Kiber",
        "active_color": "&H007FFF00",
        "base_color": "&H00FFFFFF",
        "outline_color": "&H00000000"
    },
    "fire": {
        "name": "🔴 Olovli Qizil (Action)",
        "active_color": "&H002020FF",
        "base_color": "&H00FFFFFF",
        "outline_color": "&H00000000"
    },
    "cyan": {
        "name": "🔵 Elektr Moviy (Cyan)",
        "active_color": "&H00FFFF00",
        "base_color": "&H00FFFFFF",
        "outline_color": "&H00000000"
    }
}
DEFAULT_SUBTITLE_THEME = "gold"

# 9. Fon Musiqasi Janrlari
MUSIC_GENRES = {
    "auto": "✨ Mavzuga mos avtomatik",
    "ambient_chill": "🌌 Koinot / Tinch Ambient",
    "cosmic_deep": "🪐 Chuqur Sirli / Kosmik Bas",
    "epic_inspiration": "🔥 Epik Motivatsiya / Ilhom",
    "tech_modern": "🤖 Zamonaviy Kiber / Lo-Fi",
    "suspense_drama": "🕵️‍♂️ Kutilmagan Sir / Dramatik",
    "lofi_vibes": "☕️ Xotirjam Lo-Fi / Fokus"
}
DEFAULT_MUSIC_GENRE = "auto"

# 10. AI Rasm Uslublari (Art Styles)
ART_STYLES = {
    "photoreal": {
        "name": "📸 Fotorealistik 8K (Haqiqiy kamera)",
        "prompt_suffix": ", 8k resolution, cinematic lighting, photorealistic, dramatic vertical shot, 35mm lens, award-winning cinematography",
        "model": "flux-realism"
    },
    "cinematic_3d": {
        "name": "🎬 3D Kinematik (Unreal Engine 5)",
        "prompt_suffix": ", 3d digital render, octane render, unreal engine 5, volumetric lighting, raytracing, highly detailed, vertical shot",
        "model": "flux"
    },
    "cyberpunk": {
        "name": "🌆 Kiberpank Neon (Futuristik)",
        "prompt_suffix": ", cyberpunk neon aesthetic, futuristic, glowing reflections, synthwave colors, 8k vertical shot",
        "model": "flux"
    },
    "anime": {
        "name": "✨ Anime / Makoto Shinkai Uslubi",
        "prompt_suffix": ", anime art style, makoto shinkai aesthetic, vibrant colors, detailed scenery, vertical shot",
        "model": "flux-anime"
    }
}
DEFAULT_ART_STYLE = "photoreal"

WATERMARK_TEXT = "Dasturchi: MuzaffarZed"
BRAND_NAME = "MuzaffarZed AI Studios"
