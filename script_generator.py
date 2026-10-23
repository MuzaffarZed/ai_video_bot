"""
MuzaffarZed AI Video Bot - Ssenariy Generatori (Version 3.0 Multi-Style Flagship)
Mavzu va tanlangan uslubga mos 3 kadrli viral ssenariy tuzadi (Top Faktlar, Hikoya, Motivatsiya, Ilm, Biznes).
Muallif: MuzaffarZed
"""
import os
import re
import json
import random
from typing import List, Dict
from config import GEMINI_API_KEY, VIDEO_STYLES, DEFAULT_VIDEO_STYLE

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
        """Matn qaysi tilda ekanligini avtomatik aniqlash."""
        cyrillic_chars = sum(1 for c in text if 'а' <= c.lower() <= 'я' or c.lower() in 'ёъь')
        latin_chars = sum(1 for c in text if 'a' <= c.lower() <= 'z')
        
        if cyrillic_chars > 6:
            # O'zbekcha krill yoki ruscha
            if any(w in text.lower() for w in ["ҳақида", "билан", "учун", "қандай", "нима", "сири"]):
                return "uz"
            return "ru"
        
        # Lotin tahlili
        t_low = text.lower()
        if any(w in t_low for w in ["haqida", "bilan", "uchun", "qanday", "nima", "sirlari", "qoidalari", "inson", "koinot"]):
            return "uz"
        if any(w in t_low for w in ["the", "how", "what", "secrets", "facts", "about", "world", "rules"]):
            return "en"
        return "uz"

    def generate(self, topic: str, lang: str = "uz", style: str = DEFAULT_VIDEO_STYLE) -> List[Dict]:
        """
        Berilgan mavzu va uslub bo'yicha viral video ssenariysini tuzadi.
        """
        # Avto til aniqlash
        detected_lang = self.detect_language(topic)
        final_lang = lang if lang in ["uz", "ru", "en"] else detected_lang

        if self.has_gemini:
            try:
                return self._generate_with_gemini(topic, final_lang, style)
            except Exception as e:
                print(f"[Gemini Error] {e}. Procedural generatorga o'tilmoqda.")
                return self._generate_procedural(topic, final_lang, style)
        else:
            return self._generate_procedural(topic, final_lang, style)

    def _generate_with_gemini(self, topic: str, lang: str, style: str) -> List[Dict]:
        style_instructions = {
            "top_facts": (
                "Format: 3 ta qisqa va hayratlanarli faktlar ketma-ketligi.\n"
                "1-kadr (Hook): Shok qiluvchi 1-fakt.\n"
                "2-kadr (Body): Aqlbovar qilmas 2-fakt.\n"
                "3-kadr (CTA): Eng buyuk 3-fakt va obuna bo'lishga chaqiriq."
            ),
            "story": (
                "Format: Kinematografik chuqur hikoya (Storytelling).\n"
                "1-kadr: Kutilmagan dramatik boshlanish.\n"
                "2-kadr: Voqealar rivoji va kutilmagan sir ochilishi.\n"
                "3-kadr: Hayotni o'zgartiruvchi xulosa va savol."
            ),
            "motivation": (
                "Format: Shiddatli va qat'iyatli motivatsiya (Mindset).\n"
                "1-kadr: Uyqudan uyg'otuvchi kuchli chaqiriq.\n"
                "2-kadr: G'alaba, mehnat va taslim bo'lmaslik qoidasi.\n"
                "3-kadr: Bugunoq harakat qilishga undovchi so'zlar."
            ),
            "science": (
                "Format: Ilmiy kashfiyot va koinot tadqiqoti.\n"
                "1-kadr: Koinot yoki fanning eng sirli savoli.\n"
                "2-kadr: So'nggi ilmiy tadqiqotlar va fizik haqiqat.\n"
                "3-kadr: Insoniyat kelajagi va buyuk xulosa."
            ),
            "business": (
                "Format: Boylik va biznes psixologiyasi.\n"
                "1-kadr: 99% insonlar pul haqida bilmaydigan xato.\n"
                "2-kadr: Millionerlar amal qiladigan yashirin qoida.\n"
                "3-kadr: Moliyaviy erkinlik sari 1-qadam."
            )
        }.get(style, "Top faktlar uslubida")

        lang_prompt = {
            "uz": "O'zbek tilida, nihoyatda hayajonli va viral Reels uslubida",
            "ru": "На русском языке, мощно и динамично для TikTok/Reels",
            "en": "In English, high-retention viral hook and engaging storytelling"
        }.get(lang, "O'zbek tilida")

        prompt = f"""
Siz jahonning eng mashhur video produserisiz (MrBeast va Alex Hormozi darajasida).
Mavzu: "{topic}"
Til: {lang_prompt}
Uslub: {style_instructions}

Jami davomiyligi 18-24 soniyalik, 3 ta ketma-ket kadrli TikTok/Reels ssenariysini tuzing.
Har bir kadr 1-2 jumlali lo'nda, ta'sirli va tez o'qiladigan bo'lsin.

Javobni FAQAT quyidagi JSON massivida qaytaring, ortiqcha hech qanday matn qo'shmang:
[
  {{
    "scene_num": 1,
    "text": "1-kadr matni",
    "visual_prompt": "cinematic hyper-detailed vertical 8k description in english, dramatic volumetric lighting"
  }},
  {{
    "scene_num": 2,
    "text": "2-kadr matni",
    "visual_prompt": "cinematic epic visual concept description in english, high-contrast, vibrant vertical 8k"
  }},
  {{
    "scene_num": 3,
    "text": "3-kadr matni",
    "visual_prompt": "inspiring triumphant majestic visual in english, golden sunlight, 8k photorealistic vertical"
  }}
]
"""
        response = self.model.generate_content(prompt)
        text = response.text.strip()

        # Xavfsiz Regex JSON ekstraktori
        json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if json_match:
            raw_json = json_match.group(0)
            return json.loads(raw_json)

        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    def _generate_procedural(self, topic: str, lang: str, style: str) -> List[Dict]:
        """
        AI kalitisiz har qanday sharoitda 100% ishlaydigan ko'p uslubli viral generator.
        """
        clean_topic = topic.strip()

        if lang == "uz":
            if style == "top_facts":
                s1 = f"99% insonlar {clean_topic} haqidagi bu shok faktni bilishmaydi! Birinchisi: uning kuchi kutilgandan 10 barobar ortiq!"
                s2 = f"Ikkinchi fakt: olimlar tadqiqotiga ko'ra, {clean_topic} butun dunyodagi jarayonlarni yashirin tarzda boshqaradi!"
                s3 = f"Eng hayratlanarlisi esa uchinchisi: bu sir sizning ham hayotingizni o'zgartiradi! Videoni saqlang va obuna bo'ling!"
            elif style == "motivation":
                s1 = f"To'xtang! Agar siz {clean_topic} yo'lida qiyinchilikka uchrayotgan bo'lsangiz, bu so'zlarni hoziroq eshitishingiz shart!"
                s2 = f"Yodda tuting: hech kim osonlikcha g'olib bo'lmagan. Qat'iyat va intizom har qanday to'siqni parchalab tashlaydi!"
                s3 = f"Bugunoq orzuingiz sari harakatni boshlang! Siz hamma narsaga qodirsiz, taslim bo'lmang!"
            elif style == "business":
                s1 = f"Boy insonlar {clean_topic} haqida hech qachon ochiq gapirishmaydi! Mana bu yashirin qoidani diqqat bilan eshiting:"
                s2 = f"Oddiy insonlar faqat vaqtini sarflaydi, muvaffaqiyatli insonlar esa {clean_topic} qonuniyatlariga tayanib boylik yaratadi."
                s3 = f"Kelajak aynan to'g'ri qarorlar qabul qilganlar qo'lida. Moliyaviy bilimlarni oshirish uchun obuna bo'ling!"
            elif style == "science":
                s1 = f"Koinotning eng sirli jumboqlaridan biri bu — {clean_topic}! Buni ko'rib aqlingiz lol qoladi:"
                s2 = f"Zamonaviy teleskoplar va kvant fizikasi shuni isbotladiki, {clean_topic} biz o'ylagan borliq qonunlarini butunlay o'zgartiradi."
                s3 = f"Bu sir insoniyatni yangi sivilizatsiya darajasiga olib chiqishi mumkin! Ko'proq bilish uchun bizni kuzatib boring!"
            else: # story
                s1 = f"Bir kuni butun insoniyatni hayratda qoldirgan voqea sodir bo'ldi. Hamma narsa aynan {clean_topic} dan boshlangan edi..."
                s2 = f"Hech kim kutmagan paytda uning ortidagi asl haqiqat oshkor bo'ldi va bu barcha tushunchalarni ostin-ustun qildi."
                s3 = f"Bu voqeadan chiqarilgan eng muhim saboq — haqiqat doimo g'alaba qozonishidir. Fikringizni izohlarda yozib qoldiring!"

            scenes = [
                {
                    "scene_num": 1,
                    "text": s1,
                    "visual_prompt": f"cinematic dramatic vertical shot representing {clean_topic}, 8k volumetric lighting"
                },
                {
                    "scene_num": 2,
                    "text": s2,
                    "visual_prompt": f"epic visual concept of {clean_topic}, glowing details, vertical 8k photorealistic"
                },
                {
                    "scene_num": 3,
                    "text": s3,
                    "visual_prompt": f"inspiring triumphant visual art about {clean_topic}, golden sunset, 8k vertical"
                }
            ]
        elif lang == "ru":
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
