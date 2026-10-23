"""
MuzaffarZed AI Video Bot - Ssenariy Generatori
Mavzudan jozibali 3-5 kadrli ssenariy va kadrlar vizual promptlarini tuzadi.
Muallif: MuzaffarZed
"""
import os
import json
import random
from typing import List, Dict
from config import GEMINI_API_KEY

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

    def generate(self, topic: str, lang: str = "uz") -> List[Dict]:
        """
        Berilgan mavzu bo'yicha video ssenariysini tuzadi.
        Qaytaradi: [
           {"scene_num": 1, "text": "...", "visual_prompt": "..."},
           ...
        ]
        """
        if self.has_gemini:
            try:
                return self._generate_with_gemini(topic, lang)
            except Exception as e:
                print(f"[Gemini Error] {e}. Procedural generatorga o'tilmoqda.")
                return self._generate_procedural(topic, lang)
        else:
            return self._generate_procedural(topic, lang)

    def _generate_with_gemini(self, topic: str, lang: str) -> List[Dict]:
        lang_prompt = {
            "uz": "O'zbek tilida, nihoyatda qiziqarli, zamonaviy va viral uslubda",
            "ru": "На русском языке, захватывающе и динамично для Reels/Shorts",
            "en": "In English, engaging, high-retention viral Reels/Shorts style"
        }.get(lang, "O'zbek tilida")

        prompt = f"""
Siz professional viral video rejissyori va kopiraytersiz.
Mavzu: "{topic}"
Til talabi: {lang_prompt}

Ushbu mavzu bo'yicha 3 ta ketma-ket kadrli qisqa (15-25 soniyalik) TikTok/Reels/Shorts ssenariysini tuzing.
1-kadr: Qiziqishni uyg'otuvchi kuchli Hook (savol yoki hayratlanarli fakt).
2-kadr: Asosiy sir, fakt yoki mantiqiy tushuntirish.
3-kadr: Hayratlanarli xulosa va harakatga chaqiriq (Call-to-Action).

Javobni FAQAT quyidagi JSON formatida qaytaring (hech qanday markdown yoki qo'shimcha so'zsiz):
[
  {{
    "scene_num": 1,
    "text": "Ovozlashtiriladigan qisqa 1-2 jumlali matn",
    "visual_prompt": "cinematic hyper-detailed vertical image description in english for AI image generator"
  }},
  {{
    "scene_num": 2,
    "text": "Ovozlashtiriladigan asosiy fakt matni",
    "visual_prompt": "cinematic hyper-detailed vertical image description in english"
  }},
  {{
    "scene_num": 3,
    "text": "Xulosa va harakatga chaqiruv matni",
    "visual_prompt": "cinematic hyper-detailed vertical image description in english"
  }}
]
"""
        response = self.model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        data = json.loads(text)
        return data

    def _generate_procedural(self, topic: str, lang: str) -> List[Dict]:
        """
        API kalitsiz ham 100% ishlaydigan aqlli ssenariy generatori.
        """
        clean_topic = topic.strip()
        
        # O'zbekcha aqlli shablonlar
        if lang == "uz":
            scenes = [
                {
                    "scene_num": 1,
                    "text": f"Siz hech {clean_topic} haqidagi eng hayratlanarli haqiqatni eshitganmisiz? Bu ko'pchilikni lol qoldiradi!",
                    "visual_prompt": f"cinematic mysterious vertical shot representing {clean_topic}, dramatic lighting, 8k, hyperrealistic"
                },
                {
                    "scene_num": 2,
                    "text": f"Olimlarning tadqiqotlariga ko'ra, {clean_topic} insoniyat tasavvuridan ancha chuqurroq va qudratliroq kuchga ega.",
                    "visual_prompt": f"epic visual concept of {clean_topic}, high-tech futuristic elements, vibrant neon glow, vertical framing"
                },
                {
                    "scene_num": 3,
                    "text": f"Bu haqda do'stlaringizga ham ulashing va yangi kashfiyotlar uchun bizni kuzatib boring!",
                    "visual_prompt": f"inspiring triumphant visual art about {clean_topic}, golden hour sunlight, majestic, 8k vertical"
                }
            ]
        elif lang == "ru":
            scenes = [
                {
                    "scene_num": 1,
                    "text": f"Вы когда-нибудь задумывались, что на самом деле скрывает тема {clean_topic}? Этот факт вас поразит!",
                    "visual_prompt": f"cinematic mysterious vertical shot representing {clean_topic}, dramatic lighting, 8k, photorealistic"
                },
                {
                    "scene_num": 2,
                    "text": f"Учёные доказали, что {clean_topic} таит в себе невероятные возможности, меняющие наше представление о мире.",
                    "visual_prompt": f"epic visual concept of {clean_topic}, high-tech futuristic elements, vibrant glow, vertical"
                },
                {
                    "scene_num": 3,
                    "text": f"Поделитесь этим видео с друзьями и подписывайтесь, чтобы не пропустить самое интересное!",
                    "visual_prompt": f"inspiring triumphant vertical visual about {clean_topic}, majestic lighting, 8k"
                }
            ]
        else: # en
            scenes = [
                {
                    "scene_num": 1,
                    "text": f"Did you know the shocking truth about {clean_topic}? This will completely blow your mind!",
                    "visual_prompt": f"cinematic mysterious vertical shot representing {clean_topic}, dramatic volumetric lighting, 8k, photorealistic"
                },
                {
                    "scene_num": 2,
                    "text": f"Recent discoveries reveal that {clean_topic} is far more fascinating and powerful than anyone previously imagined.",
                    "visual_prompt": f"epic visual concept of {clean_topic}, cosmic futuristic energy, vibrant colors, vertical wallpaper"
                },
                {
                    "scene_num": 3,
                    "text": f"Share this with someone who needs to see it, and follow for more mind-blowing discoveries!",
                    "visual_prompt": f"inspiring majestic vertical scene about {clean_topic}, golden rays, hyper-detailed, 8k"
                }
            ]
            
        return scenes
