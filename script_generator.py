"""
MuzaffarZed AI Video Bot - Ssenariy Generatori (Version 9.0 Quantum AI & Podcast Dialogue)
Mavzu bo'yicha 3 bosqichli AI (Gemini 2.0 -> Pollinations AI Text -> Procedural), Podkast-Dialog va SEO.
Muallif: MuzaffarZed
"""
import os
import re
import json
import random
import urllib.request
import urllib.parse
from typing import List, Dict, Optional
from config import (
    GEMINI_API_KEY, VIDEO_STYLES, DEFAULT_VIDEO_STYLE, DURATIONS, DEFAULT_DURATION,
    VOICE_MODES, DEFAULT_VOICE_MODE
)

def transliterate_uzbek(text: str) -> str:
    """O'zbekcha kirill yozuvini fonetik jihatdan benuqson lotin yozuviga o'girish."""
    mapping = {
        'Ў': "O'", 'ў': "o'", 'Ғ': "G'", 'ғ': "g'", 'Ш': "Sh", 'ш': "sh",
        'Ч': "Ch", 'ч': "ch", 'Ё': "Yo", 'ё': "yo", 'Ю': "Yu", 'ю': "yu",
        'Я': "Ya", 'я': "ya", 'Қ': "Q",  'қ': "q",  'Ҳ': "H",  'ҳ': "h",
        'А': "A",  'а': "a",  'Б': "B",  'б': "b",  'В': "V",  'в': "v",
        'Г': "G",  'г': "g",  'Д': "D",  'д': "d",  'Е': "E",  'е': "e",
        'Ж': "J",  'ж': "j",  'З': "Z",  'з': "z",  'И': "I",  'и': "i",
        'Й': "Y",  'й': "y",  'К': "K",  'к': "k",  'Л': "L",  'л': "l",
        'М': "M",  'м': "m",  'Н': "N",  'н': "n",  'О': "O",  'о': "o",
        'П': "P",  'п': "p",  'Р': "R",  'р': "r",  'С': "S",  'с': "s",
        'Т': "T",  'т': "t",  'У': "U",  'у': "u",  'Ф': "F",  'ф': "f",
        'Х': "X",  'х': "x",  'Ц': "Ts", 'ц': "ts", 'Щ': "Sh", 'щ': "sh",
        'Ъ': "'",  'ъ': "'",  'Ь': "",   'ь': "",   'Э': "E",  'э': "e"
    }
    return "".join(mapping.get(ch, ch) for ch in text)

# Fonetik talaffuz va sonlarni to'liq so'zga aylantirish (O'zbek tili uchun)
ONES_UZ = ['', 'bir', 'ikki', 'uch', "to'rt", 'besh', 'olti', 'yetti', 'sakkiz', "to'qqiz"]
TENS_UZ = ['', "o'n", 'yigirma', "o'ttiz", 'qirq', 'ellik', 'oltmish', 'yetmish', 'sakson', "to'qson"]
SCALES_UZ = ['', 'ming', 'million', 'milliard', 'trillion']

def uzbek_number_to_words(n: int) -> str:
    """Ixtiyoriy butun sonni o'zbekcha yozma so'z shakliga o'giradi (0..trillion)."""
    if n == 0:
        return 'nol'
    if n < 0:
        return 'minus ' + uzbek_number_to_words(-n)
    parts = []
    chunk_idx = 0
    while n > 0:
        chunk = n % 1000
        if chunk > 0:
            c_parts = []
            h = chunk // 100
            t = (chunk % 100) // 10
            u = chunk % 10
            if h > 0:
                if h == 1:
                    c_parts.append('bir yuz')
                else:
                    c_parts.append(ONES_UZ[h] + ' yuz')
            if t > 0:
                c_parts.append(TENS_UZ[t])
            if u > 0:
                c_parts.append(ONES_UZ[u])
            chunk_str = ' '.join(c_parts)
            if chunk_idx > 0 and SCALES_UZ[chunk_idx]:
                chunk_str += ' ' + SCALES_UZ[chunk_idx]
            parts.append(chunk_str)
        n //= 1000
        chunk_idx += 1
    return ' '.join(reversed(parts)).strip()

def to_uzbek_ordinal(words: str) -> str:
    """So'z bilan ifodalangan sonni tartib songa aylantiradi (-nchi / -inchi)."""
    words = words.strip()
    if not words:
        return words
    last_word = words.split()[-1].lower()
    if last_word.endswith(('a', 'e', 'i', 'o', 'u', "o'")):
        return words + 'nchi'
    return words + 'inchi'

def phonetic_uzbek_normalize(text: str) -> str:
    """
    O'zbek tili nutq sintezi (TTS) uchun mukammal fonetik normalizatsiya:
    1. Kirillchadan lotinchaga transliteratsiya (agar mavjud bo'lsa)
    2. Noaniq apostrof, tirnoq va tirelarni standartlashtirish
    3. Valyutalar ($100 -> bir yuz dollar, 50€ -> ellik yevro)
    4. Foizlar (99% -> to'qson to'qqiz foiz)
    5. Tartib sonlar (2026-yil -> ikki ming yigirma oltinchi yilda, 1-o'rin -> birinchi o'rin)
    6. Oraliq sonlar (5-10 -> besh dan o'n gacha)
    7. Zamonaviy texnologik va ijtimoiy tarmoq atamalari (AI, IT, ChatGPT, YouTube, TikTok, 4K)
    8. Barcha mustaqil sonlarni to'liq so'zga aylantirish.
    """
    if not text:
        return ''
    if any('а' <= c.lower() <= 'я' or c.lower() in 'ўғҳқё' for c in text):
        text = transliterate_uzbek(text)

    t = text
    # Standartlashtirish
    t = t.replace('’', "'").replace('‘', "'").replace('ʻ', "'").replace('`', "'").replace('´', "'")
    t = t.replace('“', '"').replace('”', '"').replace('«', '"').replace('»', '"')
    t = t.replace('—', ' - ').replace('–', ' - ').replace('…', ', ').replace('...', ', ')
    
    # Valyutalar
    t = re.sub(r'\$\s*(\d+)', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} dollar", t)
    t = re.sub(r'(\d+)\s*\$', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} dollar", t)
    t = re.sub(r'€\s*(\d+)', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} yevro", t)
    t = re.sub(r'(\d+)\s*€', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} yevro", t)

    # Foiz (%)
    t = re.sub(r'%\s*(\d+)', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} foiz", t)
    t = re.sub(r'(\d+)\s*%', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} foiz", t)

    # Tartib sonlar va yillar: 2026-yil, 21-asr, 1-chi, 2-nchi
    t = re.sub(r'\b(\d+)-(?:chi|nchi|inchi)\b', lambda m: to_uzbek_ordinal(uzbek_number_to_words(int(m.group(1)))), t, flags=re.IGNORECASE)
    t = re.sub(r'\b(\d+)-yil(da)?\b', lambda m: f"{to_uzbek_ordinal(uzbek_number_to_words(int(m.group(1))))} yil{'da' if m.group(2) else ''}", t, flags=re.IGNORECASE)
    t = re.sub(r'\b(\d+)-asr(da)?\b', lambda m: f"{to_uzbek_ordinal(uzbek_number_to_words(int(m.group(1))))} asr{'da' if m.group(2) else ''}", t, flags=re.IGNORECASE)

    # Qo'shma tartib sonlar: 1-o'rinda, 2-qism, 3-bosqich, 1-qadam
    t = re.sub(
        r"\b(\d+)-(o['\u02bb]?rin(?:da)?|qism|bosqich|qadam|dars|savol|bob|sinf|kurs|avlod|kun)\b",
        lambda m: f"{to_uzbek_ordinal(uzbek_number_to_words(int(m.group(1))))} {m.group(2)}",
        t,
        flags=re.IGNORECASE
    )

    # Oraliq sonlar: 5-10
    t = re.sub(r'\b(\d+)\s*-\s*(\d+)\b', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} dan {uzbek_number_to_words(int(m.group(2)))} gacha", t)

    # Kasr sonlar (2.5 -> ikki butun o'ndan besh, 3.14 -> uch butun yuzdan o'n to'rt)
    def _repl_decimal(m):
        whole = int(m.group(1))
        dec = m.group(2)
        dec_len = len(dec)
        dec_val = int(dec)
        scale = "o'ndan" if dec_len == 1 else ("yuzdan" if dec_len == 2 else "mingdan")
        return f"{uzbek_number_to_words(whole)} butun {scale} {uzbek_number_to_words(dec_val)}"
    t = re.sub(r'\b(\d+)[.,](\d{1,3})\b', _repl_decimal, t)

    # Vaqt formatlari (14:30 -> o'n to'rt o'ttiz, 08:45 -> sakkiz qirq besh)
    t = re.sub(
        r'\b(\d{1,2}):(\d{2})\b',
        lambda m: f"{uzbek_number_to_words(int(m.group(1)))} {uzbek_number_to_words(int(m.group(2)))}",
        t
    )

    # O'lchov birliklari, tezlik va maydon
    t = re.sub(r'(\d+)\s*km/s(?:oat)?\b', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} kilometr soatiga", t)
    t = re.sub(r'(\d+)\s*(?:m²|kv\.?\s*m)\b', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} kvadrat metr", t)
    t = re.sub(r'(\d+)\s*(?:m³|kub\s*m)\b', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} kub metr", t)
    t = re.sub(r'(\d+)\s*°C\b', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} gradus selsiy", t)
    t = re.sub(r'(\d+)\s*so[\'\u02bb]?m\b', lambda m: f"{uzbek_number_to_words(int(m.group(1)))} so'm", t)

    # Tashkilot, davlat va format qisqartmalari
    t = re.sub(r'\bAQSH\b', "Amerika Qo'shma Shtatlari", t)
    t = re.sub(r'\bBMT\b', 'Be-Em-Te', t)
    t = re.sub(r'\bMDH\b', 'Em-De-Ha', t)
    t = re.sub(r"\bO'zR\b", "O'zbekiston Respublikasi", t)
    t = re.sub(r'\bVIP\b', 'vi-ay-pi', t)
    t = re.sub(r'\bSMS\b', 'es-em-es', t)
    t = re.sub(r'\bPDF\b', 'pe-de-ef', t)

    # Zamonaviy texnologik va platforma atamalari
    t = re.sub(r'\bAI\b', 'ey-ay', t)
    t = re.sub(r'\bIT\b', 'ay-ti', t)
    t = re.sub(r'\bChatGPT\b', 'Chat-Ji-Pi-Ti', t, flags=re.IGNORECASE)
    t = re.sub(r'\bGPT-?4\b', "Ji-Pi-Ti to'rt", t, flags=re.IGNORECASE)
    t = re.sub(r'\bGPT\b', 'Ji-Pi-Ti', t, flags=re.IGNORECASE)
    t = re.sub(r'\bCEO\b', 'si-i-o', t, flags=re.IGNORECASE)
    t = re.sub(r'\bWi-?Fi\b', 'vay-fay', t, flags=re.IGNORECASE)
    t = re.sub(r'\bYouTube\b', 'Yutyub', t, flags=re.IGNORECASE)
    t = re.sub(r'\bTikTok\b', 'Tik-Tok', t, flags=re.IGNORECASE)
    t = re.sub(r'\b3D\b', 'uch de', t, flags=re.IGNORECASE)
    t = re.sub(r'\b4K\b', "to'rt ka", t, flags=re.IGNORECASE)
    t = re.sub(r'\bHD\b', 'eych di', t, flags=re.IGNORECASE)

    # Barcha qolgan mustaqil sonlar
    t = re.sub(r'\b(\d+)\b', lambda m: uzbek_number_to_words(int(m.group(1))), t)

    # Jonli nutq nafas olish pauzalari (Natural breath pauses at coordinating words)
    t = re.sub(r'([^\s,.;:!?])\s+(chunki|lekin|ammo|biroq|negaki)\b', r'\1, \2', t, flags=re.IGNORECASE)

    # Tinish belgilarini tozalash va ortiqcha bo'shliqlarni olib tashlash
    t = re.sub(r'\?{2,}', '?', t)
    t = re.sub(r'!{2,}', '!', t)
    t = re.sub(r',+', ',', t)
    t = re.sub(r'\s+([,.;:!?])', r'\1', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# Ssenariy generatori uchun mintaqaviy ohang va shevaviy drayv ko'rsatmalari
CADENCE_DIALECT_PROMPTS = {
    "vodiy_viral": "Nutq ohangi: Vodiy jonli va chaqqon Reels drayvi. Jo'shqin, qiziqarli va hissiyotli jumlalar (masalan: 'Qani, do'stlar, buni qarang!', 'Ajoyib-a!', 'Hozirroq sinab ko'ring!').",
    "toshkent_adabiy": "Nutq ohangi: Toshkent adabiy tili me'yori, televideniye va madaniyatli diksiya. Jiddiy, vazmin, sof adabiy va aniq mantiqiy jumlalar (masalan: 'Hurmatli tomoshabinlar...', 'Qayd etish joizki...', 'Xulosa o'rnida...').",
    "samarqand_epik": "Nutq ohangi: Samarqand va Buxoro epik hikoyachilik salobati, qadimiy Sharqona donishmandlik. Vazminlik, falsafiy teranlik va ibratli jumlalar (masalan: 'Qadim zamonlardan buyon...', 'Donolar aytganidek...', 'Tafakkur qiling...').",
    "xorazm_shirin": "Nutq ohangi: Xorazmcha samimiy, musiqiy va jozibador intonatsiya. Xalqona, iliq va mehmondo'st iboralar (masalan: 'Valaykum assalom, aziz og'alar!', 'Buni qaranglar-a!', 'Bundayini hali ko'rmagansiz!').",
    "voha_baxshi": "Nutq ohangi: Qashqadaryo va Surxondaryo vohasiga xos mardona, baxshiyona va salobatli doston ohangi (masalan: 'Ey do'st, bu elning sirlaridan xabardormisiz?', 'Mardonavor qadam tashlang!', 'Tog'lar sadosi shuni aytadi...').",
    "city_podcast": "Nutq ohangi: Toshkent City zamonaviy biznes va erkin IT podkast suhbati. Samimiy, do'stona, professional va hayotiy iboralar (masalan: 'Keling, ochiqchasiga gaplashamiz', 'Aslida esa...', 'Ko'rib turganingizdek...').",
    "koinot_mystic": "Nutq ohangi: Koinot sirlari, mistik chuqurlik va hayratlantiruvchi doku intonatsiyasi. Tasavvurni uyg'otuvchi, sirli va ehtiromli jumlalar (masalan: 'Tasavvur qilib ko'ring...', 'Koinotning cheksiz qa'rida...', 'Insoniyat hali yecholmagan jumboq...').",
    "trailer_power": "Nutq ohangi: Gollivudcha jangovar shijoat va qudratli motivatsiya. Qisqa, zarbali, kuchli va qat'iy chaqiriqlar (masalan: 'To'xtama!', 'Bugun sening kuning!', 'G'alaba faqat harakatda!')."
}

class ScriptGenerator:
    def __init__(self):
        self.has_gemini = bool(GEMINI_API_KEY)
        if self.has_gemini:
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                print(f"[Warning] Gemini yuklanmadi: {e}. Fallback rejim ishlatiladi.")
                self.has_gemini = False

    @staticmethod
    def detect_language(text: str) -> str:
        cyrillic_chars = sum(1 for c in text if 'а' <= c.lower() <= 'я' or c.lower() in 'ёъь')
        if cyrillic_chars > 5:
            if any(w in text.lower() for w in ["ҳақида", "билан", "учун", "қандай", "нима", "сири"]):
                return "uz"
            return "ru"
        
        t_low = text.lower()
        if any(w in t_low for w in ["haqida", "bilan", "uchun", "qanday", "nima", "sirlari", "qoidalari", "inson", "koinot"]):
            return "uz"
        if any(w in t_low for w in ["the", "how", "what", "secrets", "facts", "about", "world", "rules"]):
            return "en"
        return "uz"

    @staticmethod
    def expand_user_prompt(topic: str, lang: str = "uz") -> str:
        """
        Agar foydalanuvchi juda qisqa (1-2 so'z) kiritgan bo'lsa, uni algoritmlar uchun jozibali viral mavzuga aylantiradi.
        """
        raw = topic.strip()
        words = raw.split()
        if len(words) > 3 or len(raw) > 18:
            return raw

        expansions = {
            "mars": {
                "uz": "Mars sayyorasida insoniyatdan yashirilgan 3 ta sirli haqiqat",
                "ru": "3 шокирующие тайны планеты Марс, о которых молчат ученые",
                "en": "3 Mind-Blowing Secrets Hidden on Planet Mars"
            },
            "pul": {
                "uz": "Dunyodagi eng boy 1% insonlarning sirli pul qonuniyati",
                "ru": "Главный закон денег, о котором знают только богатые",
                "en": "The Secret Rule of Money That the Top 1% Never Tell You"
            },
            "koinot": {
                "uz": "Koinotning inson aqlini shoshirib qo'yuvchi eng sirli hodisalari",
                "ru": "Самые загадочные и пугающие явления в глубинах космоса",
                "en": "The Most Mysterious and Terrifying Phenomena in Deep Space"
            },
            "vaqt": {
                "uz": "Inson hayotidagi eng qimmatli narsa bu vaqt siri",
                "ru": "Почему время — самый ценный ресурс в жизни каждого человека",
                "en": "Why Time is the Most Valuable Currency in Human Life"
            },
            "ai": {
                "uz": "Sun'iy intellekt kelajakda qaysi kasblarni butunlay yo'q qiladi?",
                "ru": "Как искусственный интеллект изменит мир уже к 2027 году",
                "en": "How Artificial Intelligence Will Transform Human Life Forever"
            }
        }

        key = "".join(c for c in raw.lower() if c.isalnum())
        if key in expansions and lang in expansions[key]:
            return expansions[key][lang]

        if lang == "ru":
            return f"{raw} — шокирующие факты, которые изменят ваше мышление"
        elif lang == "en":
            return f"The Untold Truth About {raw} That Will Blow Your Mind"
        else:
            return f"{raw} haqida 99% insonlar bilmaydigan eng qiziqarli haqiqatlar"

    def generate(
        self,
        topic: str,
        lang: str = "uz",
        style: str = DEFAULT_VIDEO_STYLE,
        duration_key: str = DEFAULT_DURATION,
        voice_mode: str = DEFAULT_VOICE_MODE
    ) -> List[Dict]:
        detected_lang = self.detect_language(topic)
        final_lang = lang if lang in ["uz", "ru", "en"] else detected_lang
        final_topic = self.expand_user_prompt(topic, final_lang)

        dur_info = DURATIONS.get(duration_key, DURATIONS[DEFAULT_DURATION])
        scene_count = dur_info.get("scene_count", 3)

        # 1-Bosqich: Gemini 2.0 Flash (agar API kalit mavjud bo'lsa)
        if self.has_gemini:
            try:
                return self._generate_with_gemini(final_topic, final_lang, style, scene_count, voice_mode)
            except Exception as e:
                print(f"[Gemini Error] {e}. Pollinations AI ga o'tilmoqda.")

        # 2-Bosqich: Pollinations AI Text (bepul, onlayn sun'iy intellekt)
        try:
            return self._generate_with_pollinations(final_topic, final_lang, style, scene_count, voice_mode)
        except Exception as e:
            print(f"[Pollinations Text Error] {e}. Procedural generatorga o'tilmoqda.")

        # 3-Bosqich: Oflayn protsedural generator (100% ishonchli zaxira)
        return self._generate_procedural(final_topic, final_lang, style, scene_count, voice_mode)

    def _generate_with_pollinations(self, topic: str, lang: str, style: str, scene_count: int, voice_mode: str = DEFAULT_VOICE_MODE) -> List[Dict]:
        """Pollinations bepul ochiq AI matn modeli orqali ssenariy yaratish."""
        lang_instruction = {
            "uz": "O'zbek tilida, nihoyatda hayajonli va viral Reels uslubida",
            "ru": "На русском языке, мощно и динамично для TikTok/Reels",
            "en": "In English, high-retention viral hook and engaging storytelling"
        }.get(lang, "O'zbek tilida")

        cadence_guide = CADENCE_DIALECT_PROMPTS.get(voice_mode, "")

        prompt = (
            f"Siz professional video ssenaristisiz. Mavzu: '{topic}'. Til: {lang_instruction}. Uslub: {style}. "
            f"{cadence_guide} "
            f"AYNAN {scene_count} ta kadr yozing. 1-kadr: kuchli hook. O'rta: shok faktlar. Oxirgi: CTA. "
            f"Javobni FAQAT quyidagi JSON massivida qaytaring (hech qanday markdown yoki tushuntirishsiz): "
            f"[{{\"scene_num\": 1, \"text\": \"1-kadr matni\", \"visual_prompt\": \"cinematic vertical 8k visual prompt in english\"}}]"
        )
        url = "https://text.pollinations.ai/" + urllib.parse.quote(prompt)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=14) as resp:
            content = resp.read().decode("utf-8")

        m = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
        if m:
            data = json.loads(m.group(0))
            if isinstance(data, list) and len(data) >= 2:
                result = []
                for idx, sc in enumerate(data[:scene_count]):
                    result.append({
                        "scene_num": idx + 1,
                        "text": str(sc.get("text", topic)),
                        "visual_prompt": str(sc.get("visual_prompt", f"cinematic dramatic vertical 8k concept of {topic}, scene {idx+1}"))
                    })
                if len(result) == scene_count:
                    return result
        raise ValueError("Pollinations AI noto'g'ri JSON qaytardi")

    def _generate_with_gemini(self, topic: str, lang: str, style: str, scene_count: int, voice_mode: str = DEFAULT_VOICE_MODE) -> List[Dict]:
        lang_prompt = {
            "uz": "O'zbek tilida, nihoyatda hayajonli va viral Reels uslubida",
            "ru": "На русском языке, мощно и динамично для TikTok/Reels",
            "en": "In English, high-retention viral hook and engaging storytelling"
        }.get(lang, "O'zbek tilida")

        cadence_guide = CADENCE_DIALECT_PROMPTS.get(voice_mode, "")

        prompt = f"""
Siz jahon darajasidagi video produserisiz (MrBeast va Alex Hormozi darajasida).
Mavzu: "{topic}"
Til: {lang_prompt}
Uslub: {style}
{cadence_guide}
Kadrlar soni: AYNAN {scene_count} ta ketma-ket kadr!

Har bir kadr 1-2 jumlali lo'nda, ta'sirli va tez o'qiladigan bo'lsin.
1-kadr (Hook): Shok qiluvchi birinchi 2 soniya.
O'rta kadrlar: Asosiy faktlar, sir va voqealar rivoji.
Oxirgi kadr (CTA): Kuchli xulosa va obuna bo'lishga chaqiriq.

Javobni FAQAT quyidagi JSON massivida qaytaring, ortiqcha hech qanday matn qo'shmang:
[
  {{
    "scene_num": 1,
    "text": "1-kadr matni",
    "visual_prompt": "cinematic hyper-detailed vertical 8k visual prompt in english"
  }}
]
"""
        response = self.model.generate_content(prompt)
        text = response.text.strip()

        json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if json_match:
            raw_json = json_match.group(0)
            res = json.loads(raw_json)
            if len(res) == scene_count:
                return res

        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    def _generate_procedural(self, topic: str, lang: str, style: str, scene_count: int, voice_mode: str = DEFAULT_VOICE_MODE) -> List[Dict]:
        clean_topic = transliterate_uzbek(topic.strip()) if lang == "uz" else topic.strip()

        if lang == "uz":
            if style == "podcast_dialogue":
                if voice_mode == "samarqand_epik":
                    dialogues = [
                        (1, f"Aytingchi, {clean_topic} ortidagi azaliy hikmat va qadimiy sir nimada?"),
                        (2, f"Rivoyatlarda aytilishicha, bu insoniyat sabr-bardoshini sinovchi buyuk saboqdir!"),
                        (1, f"Darhaqiqat, buni anglagan inson hayotida mislsiz najot va yuksaklik topadi."),
                        (2, f"To'g'ri aytdingiz. Har bir o'tgan kun bizga yangi tafakkur eshigini ochadi!"),
                        (1, f"Ushbu hikmatni do'stlaringizga ulashing va yangi falsafiy bilimlarga ega bo'lish uchun obuna bo'ling!")
                    ]
                elif voice_mode == "vodiy_viral":
                    dialogues = [
                        (1, f"Qarang, {clean_topic} haqidagi bu shok sirni eshitganmisiz? Odamlar bu haqda bilishmaydi!"),
                        (2, f"Yo'g'e, rostdanmi?! Qanaqa sir ekan, tezroq ayting-chi!"),
                        (1, f"Buni qarang: {clean_topic} kuchi biz o'ylagandan 10 barobar kuchliroq ekan!"),
                        (2, f"Ana xolos! Demak buni hamma bilishi shart ekan-da!"),
                        (1, f"Albatta! Do'stlarga ham tezda yuboring va eng drayvli faktlar uchun bizga obuna bo'ling!")
                    ]
                elif voice_mode == "city_podcast":
                    dialogues = [
                        (1, f"Do'stlar, bugun {clean_topic} haqidagi eng katta mifni ochamiz. Ko'pchilik buni noto'g'ri tushunadi."),
                        (2, f"Ha, ayniqsa boshlovchilar bu borada eng ko'p xatolarga yo'l qo'yishadi. Sababi nima?"),
                        (1, f"Sababi oddiy: tizimli yondashuv yo'qligida! {clean_topic} to'g'ri strategiya bilan o'rganilsa, natija 10x bo'ladi."),
                        (2, f"Mutlaqo qo'shilaman. Zamonaviy bozorda aynan mana shu amaliy tajriba qadrlanadi!"),
                        (1, f"Kanalimizga obuna bo'ling va eng so'nggi biznes sirlarini biz bilan birga kuzatib boring!")
                    ]
                elif voice_mode == "xorazm_shirin":
                    dialogues = [
                        (1, f"Og'ajon, {clean_topic} haqidagi bu ajabtovur sirni eshitganmidingiz?"),
                        (2, f"Yo'g'-e, na gap ekan, tezroq aytib bering-chi!"),
                        (1, f"Qarang-a, {clean_topic} aslida butun dunyoni lol qoldiradigan darajada qudratli ekan!"),
                        (2, f"Zo'r bo'pti-ku! Barcha og'a-inilarimizga bu bilimlar judayam asqotadi!"),
                        (1, f"Albatta! Videoni yaqinlarga ham ulashing va bizga obuna bo'ling!")
                    ]
                elif voice_mode == "voha_baxshi":
                    dialogues = [
                        (1, f"Ey do'stim, {clean_topic} ortidagi mardona haqiqatni bilasizmi?"),
                        (2, f"Albatta bilishni istayman, bu qanday dostoniy hikmat ekan?"),
                        (1, f"Tog'lar guvohki, {clean_topic} yo'lidagi har bir qadam insonni buyuklikka yetaklaydi!"),
                        (2, f"Tasanno! Haqiqiy mardlarga xos qat'iyat mana shunday bo'ladi!"),
                        (1, f"El-yurtimiz bilan bu bilimlarni baham ko'ring va sahifamizga obuna bo'ling!")
                    ]
                else:
                    dialogues = [
                        (1, f"Bilasanmi, {clean_topic} haqidagi eng hayratlanarli sir nima? 99% insonlar buni bilishmaydi!"),
                        (2, f"Rostdanmi? Qiziq, aynan qanday sir haqida gapiryapsan?"),
                        (1, f"Tadqiqotlar shuni ko'rsatadiki, {clean_topic} kuchi insoniyat tasavvuridan 10 barobar ortiq!"),
                        (2, f"Ajoyib! Demak buni tushunish har birimiz uchun katta natijalar kaliti ekanda!"),
                        (1, f"Aynan shunday! Do'stlaringizga ham ulashing va har kuni yangi bilimlarga ega bo'lish uchun bizga obuna bo'ling!")
                    ]
                chosen_pairs = [dialogues[0], dialogues[1], dialogues[-1]] if scene_count <= 3 else dialogues[:scene_count]
                scenes = []
                for idx, (spk, text_block) in enumerate(chosen_pairs):
                    scenes.append({
                        "scene_num": idx + 1,
                        "speaker": spk,
                        "text": text_block,
                        "visual_prompt": f"cinematic podcast dialogue vertical 8k concept representing {clean_topic}, speaker {spk}, frame {idx+1}"
                    })
                return scenes

            elif style == "top_facts":
                # Ohang va mintaqaviy shevaga mos ochilish ilgagi (Cadence-specific Hook)
                if voice_mode == "samarqand_epik":
                    hook_fact = f"Qadim zamonlardan buyon insoniyat {clean_topic} sirlari ustida bosh qotirib kelgan..."
                elif voice_mode == "vodiy_viral":
                    hook_fact = f"Qani, do'stlar, buni qarang! {clean_topic} haqidagi bu sirni 99% insonlar bilmaydi!"
                elif voice_mode == "city_podcast":
                    hook_fact = f"Keling, {clean_topic} haqida ochiqchasiga gaplashamiz. Asl haqiqat mutlaqo boshqacha!"
                elif voice_mode == "koinot_mystic":
                    hook_fact = f"Tasavvur qilib ko'ring... {clean_topic} qa'rida insoniyat hali yecholmagan buyuk sir yashiringan..."
                elif voice_mode == "trailer_power":
                    hook_fact = f"To'xtang! {clean_topic} sizning butun kelajagingizni o'zgartirishi mumkin!"
                elif voice_mode == "toshkent_adabiy":
                    hook_fact = f"Hurmatli tomoshabinlar, bugun {clean_topic} haqidagi eng muhim va ishonchli faktlarni tahlil qilamiz."
                elif voice_mode == "xorazm_shirin":
                    hook_fact = f"Valaykum assalom, og'alar va yangalar! Qani qaranglar-a, {clean_topic} haqidagi bu ajoyib sirni!"
                elif voice_mode == "voha_baxshi":
                    hook_fact = f"Ey mardlar eli, quloq tuting! {clean_topic} haqidagi bu haqiqat dostonlarga tengdir!"
                else:
                    hook_fact = f"99% insonlar {clean_topic} haqidagi bu sirni bilishmaydi! Birinchisi: uning kuchi tasavvur qilinganidan 10 barobar ortiq!"

                templates = [
                    hook_fact,
                    f"Ikkinchi sir: tadqiqotlarga ko'ra, {clean_topic} zamonaviy dunyoda eng buyuk o'zgarishlar kalitiga aylanmoqda.",
                    f"Uchinchi hayratlanarli fakt: olimlar {clean_topic} ning asl qudratini endigina to'liq anglab yetmoqdalar.",
                    f"To'rtinchi haqiqat: kimki {clean_topic} qonuniyatlarini bilsa, u har qanday vaziyatda ustunlikka erishadi.",
                    f"Va eng muhimi: bu bilimlar sizning ham kelajagingizni o'zgartirishi mumkin! Do'stlaringizga ulashing va bizga obuna bo'ling!"
                ]
            elif style == "motivation":
                templates = [
                    f"To'xtang! Agar siz {clean_topic} yo'lida qiyinchilikka uchrayotgan bo'lsangiz, bu so'zlarni hoziroq tinglang!",
                    f"Hech qachon taslim bo'lmang! Har bir buyuk g'alaba aynan eng qorong'i kechalardan keyin boshlanadi.",
                    f"Intizom va qat'iyat — bu shunchaki so'zlar emas, bu sizni maqsadingizga eltuvchi yagona kuchdir.",
                    f"Atrofdagilarning shubhalariga e'tibor bermang. O'z yo'lingizda sobit turing va har kuni oldinga qadam tashlang!",
                    f"Kelajak bugungi mehnatingizga bog'liq! Hoziroq harakatni boshlang va buyuklik sari intiling!"
                ]
            elif style == "business":
                templates = [
                    f"Boy insonlar {clean_topic} haqida hech qachon ochiq gapirishmaydi! Mana bu yashirin qoidani diqqat bilan eshiting:",
                    f"Oddiy insonlar pul uchun ishlaydi, muvaffaqiyatli insonlar esa tizim va bilimlar orqali boylik yaratadi.",
                    f"Moliyaviy erkinlikning asosi — bu to'g'ri odatlar va o'z sohasini chuqur tahlil qilishdir.",
                    f"Eng katta sarmoya — bu o'z bilimingiz va tafakkuringizga kiritilgan sarmoyadir.",
                    f"Kelajak to'g'ri qaror qabul qilganlar qo'lida. Moliyaviy savodxonlikni oshirish uchun bizni kuzatib boring!"
                ]
            elif style == "science":
                templates = [
                    f"Koinotning eng sirli jumboqlaridan biri bu — {clean_topic}! Buni eshitib aqlingiz lol qoladi:",
                    f"Kvant fizikasi va zamonaviy teleskoplar borliq haqidagi barcha tasavvurlarni ostin-ustun qilib tashlamoqda.",
                    f"Har bir yangi kashfiyot biz o'ylagandan ancha murakkabroq koinot qonuniyatlarini ochib bermoqda.",
                    f"Vaqt, fazo va gravitatsiya sirlari insoniyat tafakkurini yangi bosqichga ko'tarmoqda.",
                    f"Bu kashfiyotlar kelajak sivilizatsiyasining poydevori hisoblanadi! Yangiliklardan xabardor bo'lish uchun obuna bo'ling!"
                ]
            else: # story
                templates = [
                    f"Bir kuni butun dunyoni hayratda qoldirgan voqea sodir bo'ldi. Barchasi aynan {clean_topic} dan boshlangan edi...",
                    f"Hech kim kutmagan paytda uning ortidagi asl haqiqat oshkor bo'ldi va bu barchani larzaga soldi.",
                    f"Tarix guvohlik beradiki, eng buyuk o'zgarishlar aynan shunday kutilmagan sirlar ortidan kelgan.",
                    f"Bu voqea insoniyatga o'z xatolaridan to'g'ri xulosa chiqarish kerakligini yana bir bor eslatdi.",
                    f"Siz bu haqda qanday fikrdasiz? Fikringizni izohlarda yozib qoldiring va sahifamizga obuna bo'ling!"
                ]

            if scene_count <= 3:
                chosen = [templates[0], templates[1], templates[-1]]
            elif scene_count <= 5:
                chosen = templates[:scene_count]
            else:
                extra = [f"{clean_topic} borasidagi tadqiqotlar har kuni yangi qirralarini ochib bermoqda.", f"Inson ongi har doim shunday yangiliklarga intilib yashaydi."]
                chosen = (templates + extra)[:scene_count]

            scenes = []
            for idx, text_block in enumerate(chosen):
                scenes.append({
                    "scene_num": idx + 1,
                    "text": text_block,
                    "visual_prompt": f"cinematic dramatic vertical 8k visual concept representing {clean_topic}, frame {idx+1}, epic lighting"
                })
        elif lang == "ru":
            if style == "podcast_dialogue":
                scenes = [
                    {
                        "scene_num": 1,
                        "speaker": 1,
                        "text": f"Ты знаешь самый удивительный факт про {clean_topic}? 99% людей даже не догадываются!",
                        "visual_prompt": f"cinematic podcast vertical 8k {clean_topic}"
                    },
                    {
                        "scene_num": 2,
                        "speaker": 2,
                        "text": f"Серьёзно? И в чём же заключается главный секрет?",
                        "visual_prompt": f"cinematic discussion vertical 8k {clean_topic}"
                    },
                    {
                        "scene_num": 3,
                        "speaker": 1,
                        "text": f"Учёные доказали, что это меняет привычный мир! Подписывайтесь, чтобы знать больше!",
                        "visual_prompt": f"inspiring vertical 8k {clean_topic}"
                    }
                ]
            else:
                scenes = [
                    {
                        "scene_num": 1,
                        "text": f"99% людей даже не догадываются о скрытой тайне {clean_topic}! Досмотрите это видео до конца!",
                        "visual_prompt": f"cinematic dramatic vertical shot representing {clean_topic}, 8k photorealistic"
                    },
                    {
                        "scene_num": 2,
                        "text": f"Учёные доказали, что {clean_topic} меняет законы привычного мира и открывает невероятные возможности.",
                        "visual_prompt": f"epic visual concept of {clean_topic}, futuristic energy glow, 8k vertical"
                    },
                    {
                        "scene_num": 3,
                        "text": f"Сохраняйте это видео и делитесь с друзьями, чтобы не потерять ценные знания!",
                        "visual_prompt": f"inspiring majestic vertical visual about {clean_topic}, golden rays, 8k"
                    }
                ]
        else: # en
            if style == "podcast_dialogue":
                scenes = [
                    {
                        "scene_num": 1,
                        "speaker": 1,
                        "text": f"Did you know the shocking truth about {clean_topic}? 99% of people have no clue!",
                        "visual_prompt": f"cinematic podcast vertical 8k {clean_topic}"
                    },
                    {
                        "scene_num": 2,
                        "speaker": 2,
                        "text": f"Really? Tell me, what makes it so fascinating?",
                        "visual_prompt": f"cinematic discussion vertical 8k {clean_topic}"
                    },
                    {
                        "scene_num": 3,
                        "speaker": 1,
                        "text": f"Studies prove it completely transforms our future! Share this video and follow for more insights!",
                        "visual_prompt": f"inspiring vertical 8k {clean_topic}"
                    }
                ]
            else:
                scenes = [
                    {
                        "scene_num": 1,
                        "text": f"99% of people have no idea about the hidden truth behind {clean_topic}! Listen closely right now:",
                        "visual_prompt": f"cinematic mysterious vertical shot representing {clean_topic}, dramatic lighting, 8k"
                    },
                    {
                        "scene_num": 2,
                        "text": f"Groundbreaking discoveries prove that {clean_topic} is ten times more powerful than anyone ever imagined.",
                        "visual_prompt": f"epic visual concept of {clean_topic}, cosmic futuristic energy, vibrant colors, vertical"
                    },
                    {
                        "scene_num": 3,
                        "text": f"Save this video right now and follow for more mind-blowing daily insights!",
                        "visual_prompt": f"inspiring majestic vertical scene about {clean_topic}, golden sunlight, hyper-detailed, 8k"
                    }
                ]

        return scenes

    def generate_viral_seo_package(self, topic: str, lang: str = "uz", scenes: Optional[List[Dict]] = None) -> Dict:
        """
        Instagram Reels, TikTok va YouTube Shorts uchun tayyor SEO sarlavha,
        tavsif matni, YouTube Chapters (vaqt belgilari) va 15 ta eng yuqori qamrovli (viral) hashtaglar to'plami.
        """
        clean_t = topic.strip()
        tags_uz = ["#reels", "#uzbekistan", "#toshkent", "#faktlar", "#sirlar", "#bilim", "#top", "#foydali", "#shorts", "#trend", "#uzb", "#motivatsiya", "#qiziqarli", "#rek", "#uz"]
        tags_ru = ["#рилс", "#факты", "#секреты", "#топ", "#наука", "#тренды", "#шортс", "#тикток", "#мотивация", "#полезно", "#инсайты", "#рек", "#рекомендации", "#саморазвитие", "#интересно"]
        tags_en = ["#reels", "#viral", "#shorts", "#tiktok", "#facts", "#mindblown", "#curiosity", "#trending", "#foryou", "#explore", "#motivation", "#knowledge", "#secrets", "#ai", "#fyp"]

        if lang == "ru":
            caption = f"🔥 {clean_t} — тайна, которую скрывают 99% людей! Досмотрите до конца и сохраните в закладки!"
            tags = " ".join(tags_ru)
        elif lang == "en":
            caption = f"🔥 The hidden truth about {clean_t} that 99% of people don't know! Watch until the end and share!"
            tags = " ".join(tags_en)
        else:
            caption = f"🔥 {clean_t} haqida 99% insonlar bilmaydigan haqiqat! Videoni saqlab oling va do'stlaringizga ulashing!"
            tags = " ".join(tags_uz)

        # YouTube Chapters (Vaqt belgilari va kadrma-kadr mavzular)
        if scenes:
            chapters = []
            curr_sec = 0.0
            for idx, sc in enumerate(scenes):
                m = int(curr_sec // 60)
                s = int(curr_sec % 60)
                ts = f"{m:02d}:{s:02d}"
                raw_text = sc.get("text", f"Scene {idx+1}").strip()
                short_text = raw_text[:35].rsplit(" ", 1)[0] if len(raw_text) > 35 else raw_text
                if idx == 0:
                    label = f"Kirish (Hook): {short_text}" if lang == "uz" else (f"Введение: {short_text}" if lang == "ru" else f"Hook: {short_text}")
                elif idx == len(scenes) - 1:
                    label = f"Xulosa: {short_text}" if lang == "uz" else (f"Итог: {short_text}" if lang == "ru" else f"CTA: {short_text}")
                else:
                    label = short_text
                chapters.append(f"{ts} - {label}")
                dur = float(sc.get("duration", 4.5))
                curr_sec += dur
            youtube_chapters = "\n".join(chapters)
        else:
            if lang == "ru":
                youtube_chapters = "00:00 - Введение (Hook)\n00:05 - Основные факты\n00:15 - Итог и подписка"
            elif lang == "en":
                youtube_chapters = "00:00 - Intro (Hook)\n00:05 - Main Revelations\n00:15 - Final CTA & Subscribe"
            else:
                youtube_chapters = "00:00 - Kirish (Hook)\n00:05 - Asosiy sirlar va voqealar\n00:15 - Xulosa va Obuna bo'lish"

        tiktok_tags = " ".join(tags.split()[:6])
        tiktok_caption = f"{clean_t} 🤯 {tiktok_tags}"
        instagram_caption = f"{caption}\n\n.\n{tags}"

        if lang == "ru":
            engagement_q = f"💬 Вопрос для обсуждения: А что вы думаете про {clean_t}? Напишите ваше мнение в комментариях!"
        elif lang == "en":
            engagement_q = f"💬 Discussion Question: What are your thoughts on {clean_t}? Share your perspective in the comments below!"
        else:
            engagement_q = f"💬 Muhokama uchun savol: Siz {clean_t} haqida nima deb o'ylaysiz? Fikringizni izohlarda yozib qoldiring!"

        return {
            "caption": caption,
            "hashtags": tags,
            "youtube_chapters": youtube_chapters,
            "tiktok_caption": tiktok_caption,
            "instagram_caption": instagram_caption,
            "engagement_question": engagement_q,
            "best_time": "18:30 - 21:30 (Eng yuqori faollik vaqti)"
        }

    @staticmethod
    def generate_series_plan(topic: str, lang: str = "uz") -> List[Dict]:
        """Katta mavzuni 3 qismli ketma-ket viral mini-serialga ajratish."""
        clean = topic.strip()
        if lang == "ru":
            return [
                {"part": 1, "title": f"Часть 1: Шокирующее начало — {clean}", "hook": f"99% людей не знают, с чего началось {clean}!"},
                {"part": 2, "title": f"Часть 2: Скрытая правда про {clean}", "hook": f"Секреты {clean}, которые изменили весь мир!"},
                {"part": 3, "title": f"Часть 3: Неожиданный финал {clean}", "hook": f"Главный вывод о {clean}, который перевернет ваше мышление!"}
            ]
        elif lang == "en":
            return [
                {"part": 1, "title": f"Part 1: The Shocking Origin of {clean}", "hook": f"99% of people have no idea how {clean} started!"},
                {"part": 2, "title": f"Part 2: The Hidden Truth of {clean}", "hook": f"The hidden secrets of {clean} that change everything!"},
                {"part": 3, "title": f"Part 3: The Ultimate Revelation of {clean}", "hook": f"The final mind-blowing realization about {clean}!"}
            ]
        else:
            return [
                {"part": 1, "title": f"1-Qism: {clean} — Shok Boshlanish", "hook": f"99% insonlar {clean} qanday boshlanganini bilishmaydi!"},
                {"part": 2, "title": f"2-Qism: {clean} — Yashirin Haqiqat", "hook": f"{clean} ning butun dunyodan yashirilgan eng katta siri!"},
                {"part": 3, "title": f"3-Qism: {clean} — Kutilmagan Xulosa", "hook": f"{clean} bo'yicha hayotingizni o'zgartiruvchi yakuniy haqiqat!"}
            ]

    def parse_custom_user_script(self, custom_text: str, topic: str = "Shaxsiy Mavzu") -> List[Dict]:
        """
        Foydalanuvchi kiritgan shaxsiy matnni qatorlar bo'yicha tahlil qilib kadrlar massiviga aylantiradi.
        O'ta uzun jumlalarni mantiqiy gaplarga ajratib, kadrlar balansini saqlaydi.
        """
        raw_lines = [line.strip() for line in custom_text.strip().split("\n") if len(line.strip()) >= 3]
        if not raw_lines:
            raw_lines = [custom_text.strip()]

        lines = []
        for line in raw_lines:
            if len(line) > 200 and any(p in line for p in [". ", "! ", "? "]):
                parts = re.split(r'(?<=[.!?])\s+', line)
                lines.extend([p.strip() for p in parts if len(p.strip()) >= 3])
            else:
                lines.append(line)

        lines = lines[:7]
        scenes = []
        for idx, line in enumerate(lines):
            scenes.append({
                "scene_num": idx + 1,
                "text": line,
                "visual_prompt": f"cinematic dramatic vertical 8k concept representing {topic}, scene {idx+1}, epic atmosphere"
            })
        return scenes

    @staticmethod
    def generate_trending_ideas(category: str = "all") -> List[Dict]:
        """Trenddagi viral video mavzulari to'plami."""
        catalog = {
            "space": [
                ("🌌 Jeyms Uebb kashf etgan sirli galaktikalar", "Koinot"),
                ("🕳 Qora tuynukka tushib ketsak nima bo'ladi?", "Koinot"),
                ("🪐 Marsda hayot mavjudligi haqida yangi faktlar", "Koinot")
            ],
            "business": [
                ("💰 Millionerlar hech qachon qilmaydigan 5 xato", "Biznes"),
                ("📈 2026-yilda eng daromadli sohalar", "Moliya"),
                ("🧠 Ilon Maskning kunlik intizom qoidalari", "Biznes")
            ],
            "ai": [
                ("🤖 Sun'iy intellekt 2027-yilgacha qaysi kasblarni yo'qotadi?", "AI"),
                ("🔮 Kelajak robotlari va insoniyat taqdiri", "Texnologiya"),
                ("⚡ Neyrotarmoqlar orqali kuniga daromad topish usuli", "AI")
            ],
            "motivation": [
                ("🔥 Taslim bo'lishdan oldin bu so'zlarni tinglang", "Motivatsiya"),
                ("⚡ 99% insonlarni orqada qoldiruvchi 1 ta odat", "Rivojlanish"),
                ("🦁 O'ziga bo'lgan ishonchni 10 barobar oshirish siri", "Psixologiya")
            ]
        }
        if category in catalog:
            return [{"title": t, "tag": tag} for t, tag in catalog[category]]

        all_ideas = []
        for cat_list in catalog.values():
            all_ideas.extend(cat_list)
        random.shuffle(all_ideas)
        return [{"title": t, "tag": tag} for t, tag in all_ideas[:6]]

    def translate_script(self, scenes: List[Dict], target_lang: str) -> List[Dict]:
        """
        Mavjud ssenariy kadrlarining matnini boshqa tilga (uz, ru, en) professional tarzda tarjima qiladi.
        """
        if not scenes:
            return scenes

        lang_names = {"uz": "Uzbek (Lotin)", "ru": "Russian", "en": "English"}
        target_name = lang_names.get(target_lang, "Uzbek")

        texts = [s.get("text", "") for s in scenes]
        translated_texts = None

        if self.has_gemini:
            try:
                prompt = (
                    f"You are a professional viral video scriptwriter and translator. "
                    f"Translate the following {len(texts)} narration lines into high-energy, engaging {target_name}. "
                    f"Preserve the emotional rhythm, hooks, and punchiness. "
                    f"Return ONLY a valid JSON array of {len(texts)} strings.\n\n"
                    f"Original lines:\n{json.dumps(texts, ensure_ascii=False)}"
                )
                response = self.model.generate_content(prompt)
                raw_text = response.text.strip()
                if "```json" in raw_text:
                    raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_text:
                    raw_text = raw_text.split("```")[1].split("```")[0].strip()
                data = json.loads(raw_text)
                if isinstance(data, list) and len(data) == len(scenes):
                    translated_texts = [str(t).strip() for t in data]
            except Exception as e:
                print(f"[Gemini Translate Notice] {e}")

        if not translated_texts:
            try:
                combined = " ||| ".join(texts)
                query = urllib.parse.quote(f"Translate these separated lines to {target_name}. Keep separator ' ||| ': {combined}")
                req_url = f"https://text.pollinations.ai/{query}?model=openai"
                req = urllib.request.Request(req_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    raw = response.read().decode("utf-8").strip()
                parts = raw.split("|||")
                if len(parts) == len(texts):
                    translated_texts = [p.strip() for p in parts]
            except Exception as e:
                print(f"[Pollinations Translate Notice] {e}")

        new_scenes = []
        for idx, sc in enumerate(scenes):
            new_sc = dict(sc)
            if translated_texts and idx < len(translated_texts) and len(translated_texts[idx]) > 3:
                new_text = transliterate_uzbek(translated_texts[idx]) if target_lang == "uz" else translated_texts[idx]
                new_sc["text"] = new_text
            new_scenes.append(new_sc)
        return new_scenes
