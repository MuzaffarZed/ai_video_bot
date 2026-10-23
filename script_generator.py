"""
MuzaffarZed AI Video Bot - Ssenariy Generatori (Version 2.0 Viral Hooks)
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
        Berilgan mavzu bo'yicha viral video ssenariysini tuzadi.
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
            "uz": "O'zbek tilida, nihoyatda hayajonli, 1-soniyadanoq ushlab qoluvchi viral Reels/Shorts uslubida",
            "ru": "На русском языке, с мощным вирусным хуком для TikTok/Reels",
            "en": "In English, high-retention viral hook, engaging storytelling"
        }.get(lang, "O'zbek tilida")

        prompt = f"""
Siz jahon darajasidagi viral video produserisiz (MrBeast va Hormozi uslubida).
Mavzu: "{topic}"
Til: {lang_prompt}

Ushbu mavzu bo'yicha 3 ta ketma-ket kadrli ultra-dinamik (18-25 soniyalik) TikTok/Reels ssenariysini tuzing.
1-kadr (Hook): Birinchi 2 soniyada tomoshabinni lol qoldiradigan keskin savol yoki kutilmagan sir.
2-kadr (Body): Asosiy sir, hayratlanarli ilmiy yoki amaliy dalil.
3-kadr (CTA): Fikrni o'zgartiruvchi xulosa va harakatga chaqiruv.

Javobni FAQAT quyidagi JSON formatida qaytaring:
[
  {{
    "scene_num": 1,
    "text": "1-2 jumlali kuchli Hook matni",
    "visual_prompt": "cinematic hyper-detailed vertical image description in english, dramatic volumetric lighting, 8k"
  }},
  {{
    "scene_num": 2,
    "text": "Asosiy sir va dalil matni",
    "visual_prompt": "cinematic epic visual concept description in english, high-contrast, vibrant, 8k vertical"
  }},
  {{
    "scene_num": 3,
    "text": "Xulosa va chaqiriq matni",
    "visual_prompt": "inspiring triumphant majestic visual in english, golden rays, 8k photorealistic"
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
        return json.loads(text)

    def _generate_procedural(self, topic: str, lang: str) -> List[Dict]:
        """
        Ultra-jozibali viral qoliplar (API kalitsiz 100% Zero-Defect).
        """
        clean_topic = topic.strip()

        if lang == "uz":
            hooks = [
                f"99% insonlar {clean_topic} haqidagi bu haqiqatni bilishmaydi! Diqqat bilan eshiting:",
                f"To'xtang! Agar siz {clean_topic} haqida eshitgan bo'lsangiz, asl haqiqat sizni lol qoldiradi!",
                f"Siz hech {clean_topic} insoniyat tarixini qanday o'zgartirganini o'ylab ko'rganmisiz? Bu aqlbovar qilmas sir!"
            ]
            bodies = [
                f"Olimlar va soha mutaxassislarining so'nggi kashfiyotiga ko'ra, {clean_topic} biz o'ylagandan 10 barobar kuchliroq ta'sirga ega.",
                f"Eng qizig'i shundaki, {clean_topic} zamonaviy dunyoda eng buyuk imkoniyatlar kalitiga aylanib bormoqda.",
                f"Chuqur tahlillar shuni ko'rsatadiki, {clean_topic} ning asl qudrati uning yashirin qonuniyatlarida yotadi."
            ]
            conclusions = [
                f"Ushbu videoni saqlab oling va do'stlaringizga ham ulashing! Yangi bilimlardan xabardor bo'ling!",
                f"Siz bu haqda qanday fikrdasiz? Fikringizni izohlarda yozib qoldiring va bizga obuna bo'ling!",
                f"Kelajak aynan shunday kashfiyotlar qo'lida. Ko'proq bilish uchun kuzatib boring!"
            ]

            h = random.choice(hooks)
            b = random.choice(bodies)
            c = random.choice(conclusions)

            scenes = [
                {
                    "scene_num": 1,
                    "text": h,
                    "visual_prompt": f"cinematic mysterious vertical shot of {clean_topic}, dramatic volumetric lighting, 8k, hyperrealistic"
                },
                {
                    "scene_num": 2,
                    "text": b,
                    "visual_prompt": f"epic visual concept representing {clean_topic}, high-tech futuristic elements, vibrant glow, vertical 8k"
                },
                {
                    "scene_num": 3,
                    "text": c,
                    "visual_prompt": f"inspiring triumphant visual art about {clean_topic}, golden hour sunlight, majestic, 8k vertical"
                }
            ]
        elif lang == "ru":
            scenes = [
                {
                    "scene_num": 1,
                    "text": f"99% людей даже не догадываются о скрытой тайне {clean_topic}! Досмотрите до конца!",
                    "visual_prompt": f"cinematic dramatic vertical shot representing {clean_topic}, 8k photorealistic"
                },
                {
                    "scene_num": 2,
                    "text": f"Учёные доказали, что {clean_topic} меняет законы привычного мира и открывает невероятные возможности.",
                    "visual_prompt": f"epic visual concept of {clean_topic}, futuristic energy glow, 8k vertical"
                },
                {
                    "scene_num": 3,
                    "text": f"Сохраняйте это видео и делитесь с друзьями, чтобы не потерять!",
                    "visual_prompt": f"inspiring majestic vertical visual about {clean_topic}, golden rays, 8k"
                }
            ]
        else: # en
            scenes = [
                {
                    "scene_num": 1,
                    "text": f"99% of people have no idea about the hidden truth behind {clean_topic}! Listen closely:",
                    "visual_prompt": f"cinematic mysterious vertical shot representing {clean_topic}, dramatic lighting, 8k"
                },
                {
                    "scene_num": 2,
                    "text": f"Recent scientific breakthroughs prove that {clean_topic} is ten times more powerful than anyone ever imagined.",
                    "visual_prompt": f"epic visual concept of {clean_topic}, cosmic futuristic energy, vibrant colors, vertical"
                },
                {
                    "scene_num": 3,
                    "text": f"Save this video right now and share it with someone who needs to hear this!",
                    "visual_prompt": f"inspiring majestic vertical scene about {clean_topic}, golden sunlight, hyper-detailed, 8k"
                }
            ]

        return scenes
