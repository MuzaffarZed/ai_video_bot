"""
MuzaffarZed AI Video Bot - Ssenariy Generatori (Version 2.5 Viral Retention)
Mavzudan jozibali 3 kadrli yuqori ushlab qoluvchi (Hook, Insight, CTA) ssenariy tuzadi.
Muallif: MuzaffarZed
"""
import os
import re
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
Siz jahon darajasidagi viral video produserisiz (MrBeast va Alex Hormozi uslubida).
Mavzu: "{topic}"
Til: {lang_prompt}

Ushbu mavzu bo'yicha 3 ta ketma-ket kadrli ultra-dinamik (18-24 soniyalik) TikTok/Reels ssenariysini tuzing.
1-kadr (Hook, 4 soniya): Tomoshabinni lol qoldiradigan keskin savol yoki sir.
2-kadr (Body/Insight, 8 soniya): Asosiy sir, hayratlanarli ilmiy yoki amaliy fakt.
3-kadr (CTA/Action, 5 soniya): Fikrni o'zgartiruvchi xulosa va harakatga chaqiruv.

Javobni FAQAT quyidagi JSON massivida qaytaring, ortiqcha so'z yoki markdown yozmang:
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

        # Robust Regex Parser (JSONDecodeError dan mutlaq himoya)
        json_match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if json_match:
            raw_json = json_match.group(0)
            return json.loads(raw_json)

        # Tozalash
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())

    def _generate_procedural(self, topic: str, lang: str) -> List[Dict]:
        """
        Yuqori darajadagi viral qoliplar (API kalitisiz 100% Zero-Defect).
        """
        clean_topic = topic.strip()

        if lang == "uz":
            hooks = [
                f"99% insonlar {clean_topic} haqidagi bu sirni bilishmaydi! Diqqat bilan tinglang:",
                f"To'xtang! Agar siz {clean_topic} haqida eshitgan bo'lsangiz, asl haqiqat sizni hayratda qoldiradi!",
                f"Siz hech o'ylab ko'rganmisiz, {clean_topic} hayotimizni qanchalik o'zgartirishi mumkin? Bu aqlbovar qilmas sir!",
                f"Bir daqiqa! Aynan bugun {clean_topic} haqida bilishingiz kerak bo'lgan eng muhim haqiqat ochiladi!"
            ]
            bodies = [
                f"Olimlar va yetakchi soha mutaxassislarining so'nggi tahlillari shuni ko'rsatadiki, {clean_topic} biz o'ylagandan 10 barobar kuchliroq ta'sirga ega.",
                f"Eng hayratlanarlisi shundaki, {clean_topic} ning yashirin mexanizmlari bugungi kunda eng buyuk imkoniyatlar kalitiga aylanmoqda.",
                f"Tadqiqotlarga ko'ra, kimki {clean_topic} qonuniyatlarini tushunib yetsa, u o'z sohasida mutlaq ustunlikka erishadi.",
                f"Chuqur o'rganishlar natijasida ma'lum bo'lishicha, {clean_topic} kelajak texnologiyalari va tafakkurining asosi hisoblanadi."
            ]
            conclusions = [
                f"Ushbu videoni saqlab oling va do'stlaringizga ham ulashing! Yangi bilimlardan har doim xabardor bo'ling!",
                f"Siz bu haqda qanday fikrdasiz? Fikringizni izohlarda yozib qoldiring va bizga obuna bo'lishni unutmang!",
                f"Kelajak aynan shunday yangiliklar qo'lida. O'z imkoniyatlaringizni oshirish uchun bizni kuzatib boring!",
                f"Hayotingizni o'zgartirish uchun bugunoq harakat qiling! Kanalimizga a'zo bo'ling va eng so'nggi bilimlarga ega bo'ling!"
            ]

            h = random.choice(hooks)
            b = random.choice(bodies)
            c = random.choice(conclusions)

            scenes = [
                {
                    "scene_num": 1,
                    "text": h,
                    "visual_prompt": f"cinematic mysterious vertical shot of {clean_topic}, dramatic volumetric lighting, 8k, photorealistic"
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
                    "text": f"Учёные доказали, что {clean_topic} меняет привычные законы и открывает невероятные возможности.",
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
                    "text": f"99% of people have no idea about the hidden truth behind {clean_topic}! Listen closely:",
                    "visual_prompt": f"cinematic mysterious vertical shot representing {clean_topic}, dramatic lighting, 8k"
                },
                {
                    "scene_num": 2,
                    "text": f"Recent breakthroughs prove that {clean_topic} is ten times more impactful than anyone imagined.",
                    "visual_prompt": f"epic visual concept of {clean_topic}, cosmic futuristic energy, vibrant colors, vertical"
                },
                {
                    "scene_num": 3,
                    "text": f"Save this video right now and follow for more groundbreaking insights every single day!",
                    "visual_prompt": f"inspiring majestic vertical scene about {clean_topic}, golden sunlight, hyper-detailed, 8k"
                }
            ]

        return scenes
