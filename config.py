"""
MuzaffarZed AI Video Bot - Konfiguratsiya va Sozlamalar (Singularity 18.0 Cosmic Singularity)
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

# 2. Ovoz Rejimlari, Mintaqaviy Sheva va Ohang Dinamikasi (Speech Cadence & Dialects)
VOICE_MODES = {
    "vodiy_viral": {
        "name": "⚡ Vodiy Jonli Reels (+15% jo'shqin, viral drayv)",
        "rate": "+15%",
        "pitch": "+2Hz",
        "cadence": "viral_hook",
        "desc": "Tezkor, e'tiborni tortuvchi va viral roliklar uchun jo'shqin drayv ohangi"
    },
    "toshkent_adabiy": {
        "name": "🏛 Toshkent Adabiy (Aniq diksiya, madaniy me'yor)",
        "rate": "+6%",
        "pitch": "-1Hz",
        "cadence": "literary_clean",
        "desc": "Adabiy til me'yorlari, aniq artikulyatsiya va televideniye madaniyati"
    },
    "samarqand_epik": {
        "name": "📜 Samarqand & Buxoro Epik (Vazmin rivoyat, tarix)",
        "rate": "-2%",
        "pitch": "-3Hz",
        "cadence": "epic_story",
        "desc": "Afsona, qadimiy rivoyatlar va falsafiy hikoyalar uchun chuqur salobat"
    },
    "xorazm_shirin": {
        "name": "🌟 Xorazm Musiqiy (+8% jozibali, samimiy ohang)",
        "rate": "+8%",
        "pitch": "+1Hz",
        "cadence": "xorazm_flow",
        "desc": "Xorazmcha samimiy, musiqiy va mehmondo'st xalqona intonatsiya"
    },
    "voha_baxshi": {
        "name": "🏔 Voha Baxshiyona (+5% Qashqadaryo & Surxon mardona)",
        "rate": "+5%",
        "pitch": "-2Hz",
        "cadence": "voha_epic",
        "desc": "Qashqadaryo va Surxondaryo eliga xos mardona, salobatli va baxshiyona ohang"
    },
    "city_podcast": {
        "name": "🏙 Toshkent City Podkast (+10% biznes & intervyu)",
        "rate": "+10%",
        "pitch": "+0Hz",
        "cadence": "podcast_flow",
        "desc": "Zamonaviy IT, startap va professional podkastlar uchun samimiy erkin uslub"
    },
    "koinot_mystic": {
        "name": "🌌 Sirli Koinot & Doku (-4Hz chuqur sirli bas)",
        "rate": "+3%",
        "pitch": "-4Hz",
        "cadence": "mystic_doku",
        "desc": "Ilmiy kashfiyotlar, sirli jumboqlar va koinot mavzulari uchun mistik ohang"
    },
    "trailer_power": {
        "name": "🔥 Gollivud Jangovar (+12% shiddat, kuchli motiv)",
        "rate": "+12%",
        "pitch": "-2Hz",
        "cadence": "power_action",
        "desc": "Treyler, sport, jangovar motivatsiya va qat'iy chaqiriq ohangi"
    },
    # Eski versiyalar bilan 100% moslik (Legacy Aliases)
    "reels_fast": {
        "name": "🚀 Reels Dinamik (+12% tezlik, baquvvat)",
        "rate": "+12%",
        "pitch": "-1Hz",
        "cadence": "viral_hook",
        "desc": "Standart Reels tezligi"
    },
    "cinematic_deep": {
        "name": "🎬 Kinematik Chuqur (-3Hz bas)",
        "rate": "+5%",
        "pitch": "-3Hz",
        "cadence": "mystic_doku",
        "desc": "Kinematografik chuqur ovoz"
    },
    "natural_clean": {
        "name": "🎙 Standart Tabiiy (1.0x me'yorda)",
        "rate": "+0%",
        "pitch": "+0Hz",
        "cadence": "literary_clean",
        "desc": "O'zgarishsiz standart nutq"
    },
    "energetic": {
        "name": "⚡ Energetik / TikTok (+16% tezyurar)",
        "rate": "+16%",
        "pitch": "+1Hz",
        "cadence": "viral_hook",
        "desc": "Maksimal tez va chaqqon nutq"
    }
}
DEFAULT_VOICE_MODE = "vodiy_viral"

# 2.1 Ovoz Akustikasi va Studiya DSP Effektlari (Audio Effects)
AUDIO_EFFECTS = {
    "studio_warmth": {
        "name": "🎙 Studiya Issiqligi (Broadcast EBU R128)",
        "filter": "highpass=f=80,equalizer=f=220:t=q:w=1.2:g=2.8,equalizer=f=3600:t=q:w=1.0:g=3.2,compand=attacks=0.02:decays=0.1:points=-80/-80|-25/-15|-10/-5|0/0:soft-knee=6,loudnorm=I=-16:TP=-1.5:LRA=11"
    },
    "deep_trailer": {
        "name": "🎬 Gollivud Treyleri (Sub-Bass + Reverb)",
        "filter": "highpass=f=60,equalizer=f=120:t=q:w=1.2:g=4.5,equalizer=f=3400:t=q:w=1.0:g=3.0,aecho=0.8:0.88:35:0.22,loudnorm=I=-16:TP=-1.5:LRA=11"
    },
    "radio_broadcast": {
        "name": "📻 Jonli Radio Efiri (FM Radio Filter)",
        "filter": "bandpass=f=1700:width_type=h:w=2400,equalizer=f=1200:t=q:w=1.0:g=3.0,compand=attacks=0.01:decays=0.08:points=-80/-80|-20/-6|0/0:soft-knee=6,loudnorm=I=-16:TP=-1.5:LRA=9"
    },
    "vintage_tape": {
        "name": "📼 Vintage Kassetasi (Lo-Fi Tape + Warmth)",
        "filter": "lowpass=f=4500,highpass=f=140,equalizer=f=320:t=q:w=1.2:g=2.2,loudnorm=I=-16:TP=-1.5:LRA=10"
    }
}
DEFAULT_AUDIO_EFFECT = "studio_warmth"

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
    "cinematic_35mm": {
        "name": "🎞 Gollivud 35mm (Film Grain + Vignette)",
        "filter": "eq=contrast=1.08:saturation=1.12,vignette=PI/4.8,noise=alls=6:allf=t+u"
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
    "cyber_action": "⚡️ Kiber-Dinamik / Synthwave",
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

# 11. Fon Musiqasi Balandligi (BGM Volume)
MUSIC_VOLUMES = {
    "mute": {"name": "🔇 Musiqasiz (Faqat toza nutq)", "vol": 0.0},
    "low": {"name": "🔉 Mayin fon (8%)", "vol": 0.08},
    "medium": {"name": "🔊 Standart (15%)", "vol": 0.15},
    "high": {"name": "📢 Baland (25%)", "vol": 0.25}
}
DEFAULT_MUSIC_VOLUME = "medium"

# 12. 1-Bosishda Studiya Shablonlari (Studio Presets)
STUDIO_PRESETS = {
    "tiktok_hook": {
        "name": "🔥 TikTok Viral Hook (15s, Kiberpank, Olovli)",
        "settings": {
            "style": "top_facts",
            "mode": "reels_fast",
            "theme": "fire",
            "sub_size": "large",
            "format": "9:16",
            "filter": "cyberpunk",
            "duration": "short_15",
            "music": "tech_modern",
            "art_style": "cyberpunk"
        }
    },
    "space_doku": {
        "name": "🌌 Koinot Mini-Doku (45s, Teal-Orange, Cyan)",
        "settings": {
            "style": "science",
            "mode": "cinematic_deep",
            "theme": "cyan",
            "sub_size": "medium",
            "format": "9:16",
            "filter": "teal_orange",
            "duration": "deep_45",
            "music": "cosmic_deep",
            "art_style": "photoreal"
        }
    },
    "podcast_dual": {
        "name": "🎙 Ikki Kishilik Podkast (30s, Sardor & Madina)",
        "settings": {
            "style": "podcast_dialogue",
            "mode": "natural_clean",
            "theme": "gold",
            "sub_size": "medium",
            "format": "9:16",
            "filter": "clean",
            "duration": "medium_30",
            "music": "lofi_vibes",
            "art_style": "photoreal"
        }
    },
    "youtube_wide": {
        "name": "🖥 YouTube Gorizontal (16:9, Clean HDR)",
        "settings": {
            "style": "story",
            "mode": "natural_clean",
            "theme": "gold",
            "sub_size": "small",
            "format": "16:9",
            "filter": "clean",
            "duration": "deep_45",
            "music": "ambient_chill",
            "art_style": "photoreal"
        }
    },
    "business_master": {
        "name": "💰 Biznes & Boylik (30s, Oltin, Zumrad)",
        "settings": {
            "style": "business",
            "mode": "reels_fast",
            "theme": "emerald",
            "sub_size": "medium",
            "format": "9:16",
            "filter": "golden",
            "duration": "medium_30",
            "music": "epic_inspiration",
            "art_style": "photoreal"
        }
    }
}

# 13. Kamera Harakati (Camera Motion)
CAMERA_MOTIONS = {
    "dynamic_drift": {
        "name": "🎬 Kinematik Drift (1.15x Mayin suzish)",
        "zoom": 1.15,
        "speed": 1.0,
        "mode": "drift"
    },
    "ken_burns_in": {
        "name": "🔭 Ken Burns Slow Zoom (1.0 -> 1.20x)",
        "zoom": 1.20,
        "speed": 0.8,
        "mode": "zoom_in"
    },
    "ken_burns_pan": {
        "name": "🛸 Kinematik Silliq Pan (Panorama)",
        "zoom": 1.18,
        "speed": 0.7,
        "mode": "pan_horiz"
    },
    "rapid_punch": {
        "name": "⚡️ Shok Zoom Punch (1.28x Tezkor)",
        "zoom": 1.28,
        "speed": 1.6,
        "mode": "punch"
    },
    "static_crisp": {
        "name": "📸 Tiniq Statik (1.02x Qimirlamasdan)",
        "zoom": 1.02,
        "speed": 0.0,
        "mode": "static"
    }
}
DEFAULT_CAMERA_MOTION = "dynamic_drift"

WATERMARK_TEXT = "Dasturchi: MuzaffarZed"
BRAND_NAME = "MuzaffarZed AI Studios"
