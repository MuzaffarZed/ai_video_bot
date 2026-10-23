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
from typing import List, Dict
from config import GEMINI_API_KEY, VIDEO_STYLES, DEFAULT_VIDEO_STYLE, DURATIONS, DEFAULT_DURATION

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

    def generate(
        self,
        topic: str,
        lang: str = "uz",
        style: str = DEFAULT_VIDEO_STYLE,
        duration_key: str = DEFAULT_DURATION
    ) -> List[Dict]:
        detected_lang = self.detect_language(topic)
        final_lang = lang if lang in ["uz", "ru", "en"] else detected_lang

        dur_info = DURATIONS.get(duration_key, DURATIONS[DEFAULT_DURATION])
        scene_count = dur_info.get("scene_count", 3)

        # 1-Bosqich: Gemini 2.0 Flash (agar API kalit mavjud bo'lsa)
        if self.has_gemini:
            try:
                return self._generate_with_gemini(topic, final_lang, style, scene_count)
            except Exception as e:
                print(f"[Gemini Error] {e}. Pollinations AI ga o'tilmoqda.")

        # 2-Bosqich: Pollinations AI Text (bepul, onlayn sun'iy intellekt)
        try:
            return self._generate_with_pollinations(topic, final_lang, style, scene_count)
        except Exception as e:
            print(f"[Pollinations Text Error] {e}. Procedural generatorga o'tilmoqda.")

        # 3-Bosqich: Oflayn protsedural generator (100% ishonchli zaxira)
        return self._generate_procedural(topic, final_lang, style, scene_count)

    def _generate_with_pollinations(self, topic: str, lang: str, style: str, scene_count: int) -> List[Dict]:
        """Pollinations bepul ochiq AI matn modeli orqali ssenariy yaratish."""
        lang_instruction = {
            "uz": "O'zbek tilida, nihoyatda hayajonli va viral Reels uslubida",
            "ru": "На русском языке, мощно и динамично для TikTok/Reels",
            "en": "In English, high-retention viral hook and engaging storytelling"
        }.get(lang, "O'zbek tilida")

        prompt = (
            f"Siz professional video ssenaristisiz. Mavzu: '{topic}'. Til: {lang_instruction}. Uslub: {style}. "
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

    def _generate_with_gemini(self, topic: str, lang: str, style: str, scene_count: int) -> List[Dict]:
        lang_prompt = {
            "uz": "O'zbek tilida, nihoyatda hayajonli va viral Reels uslubida",
            "ru": "На русском языке, мощно и динамично для TikTok/Reels",
            "en": "In English, high-retention viral hook and engaging storytelling"
        }.get(lang, "O'zbek tilida")

        prompt = f"""
Siz jahon darajasidagi video produserisiz (MrBeast va Alex Hormozi darajasida).
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
        clean_topic = transliterate_uzbek(topic.strip()) if lang == "uz" else topic.strip()

        if lang == "uz":
            if style == "podcast_dialogue":
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

    def generate_viral_seo_package(self, topic: str, lang: str = "uz") -> Dict:
        """
        Instagram Reels, TikTok va YouTube Shorts uchun tayyor SEO sarlavha,
        tavsif matni va 15 ta eng yuqori qamrovli (viral) hashtaglar to'plami.
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

        return {
            "caption": caption,
            "hashtags": tags,
            "best_time": "18:30 - 21:30 (Eng yuqori faollik vaqti)"
        }

    def parse_custom_user_script(self, custom_text: str, topic: str = "Shaxsiy Mavzu") -> List[Dict]:
        """
        Foydalanuvchi kiritgan shaxsiy matnni qatorlar bo'yicha tahlil qilib kadrlar massiviga aylantiradi.
        """
        lines = [line.strip() for line in custom_text.strip().split("\n") if len(line.strip()) >= 3]
        if not lines:
            lines = [custom_text.strip()]

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
