"""
MuzaffarZed AI Video Bot - Ssenariy Generatori (Version 4.0 Titanium Dynamic Scenes)
Mavzu, uslub va davomiylikka (3, 5 yoki 7 kadr) mos viral ssenariy tuzadi.
Muallif: MuzaffarZed
"""
import os
import re
import json
import random
from typing import List, Dict
from config import GEMINI_API_KEY, VIDEO_STYLES, DEFAULT_VIDEO_STYLE, DURATIONS, DEFAULT_DURATION

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

    def generate(
        self,
        topic: str,
        lang: str = "uz",
        style: str = DEFAULT_VIDEO_STYLE,
        duration_key: str = DEFAULT_DURATION
    ) -> List[Dict]:
        """
        Berilgan mavzu, uslub va davomiylik bo'yicha viral ssenariy tuzadi.
        """
        detected_lang = self.detect_language(topic)
        final_lang = lang if lang in ["uz", "ru", "en"] else detected_lang

        dur_info = DURATIONS.get(duration_key, DURATIONS[DEFAULT_DURATION])
        scene_count = dur_info.get("scene_count", 3)

        if self.has_gemini:
            try:
                return self._generate_with_gemini(topic, final_lang, style, scene_count)
            except Exception as e:
                print(f"[Gemini Error] {e}. Procedural generatorga o'tilmoqda.")
                return self._generate_procedural(topic, final_lang, style, scene_count)
        else:
            return self._generate_procedural(topic, final_lang, style, scene_count)

    def _generate_with_gemini(self, topic: str, lang: str, style: str, scene_count: int) -> List[Dict]:
        lang_prompt = {
            "uz": "O'zbek tilida, nihoyatda hayajonli va viral Reels uslubida",
            "ru": "На русском языке, мощно и динамично для TikTok/Reels",
            "en": "In English, high-retention viral hook and engaging storytelling"
        }.get(lang, "O'zbek tilida")

        prompt = f"""
Siz jahonning eng mashhur video produserisiz (MrBeast va Alex Hormozi darajasida).
Mavzu: "{topic}"
Til: {lang_prompt}
Uslub: {style}
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

    def _generate_procedural(self, topic: str, lang: str, style: str, scene_count: int) -> List[Dict]:
        """
        Har qanday sharoitda aniq {scene_count} ta viral kadr ishlab chiquvchi generator.
        """
        clean_topic = topic.strip()

        if lang == "uz":
            if style == "top_facts":
                templates = [
                    f"99% insonlar {clean_topic} haqidagi bu sirni bilishmaydi! Birinchisi: uning kuchi tasavvur qilinganidan 10 barobar ortiq!",
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

            # scene_count ga qarab tanlash
            if scene_count <= 3:
                chosen = [templates[0], templates[1], templates[-1]]
            elif scene_count <= 5:
                chosen = templates[:scene_count]
            else:
                # 7 kadr uchun kengaytirish
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
