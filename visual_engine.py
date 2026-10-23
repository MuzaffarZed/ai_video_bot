"""
MuzaffarZed AI Video Bot - Kengaytirilgan Vizual Kadrlar Dvigateli (Visual Studio 8.0 Grandmaster)
Haqiqiy Real-Time AI rasm generatsiyasi (Pollinations Flux AI), 12 toifali 4K kutubxona va fotorealistik filtr.
Muallif: MuzaffarZed
"""
import os
import time
import random
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from config import TEMP_DIR, FORMATS, DEFAULT_FORMAT, ART_STYLES, DEFAULT_ART_STYLE

class VisualEngine:
    CURATED_THEMES = {
        "space": [
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1447433819943-74a20887a81e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1446776877081-d282a0f896e2?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1506443432602-ac2fcd6f54e0?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1516339901601-2e1b62dc0c45?w=1080&h=1920&fit=crop&q=80"
        ],
        "ai": [
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507146426996-ef05306b995a?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1677442136019-21780efad99a?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1535378917042-10a22c95931a?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=1080&h=1920&fit=crop&q=80"
        ],
        "business": [
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1444723121867-7a241cacace9?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?w=1080&h=1920&fit=crop&q=80"
        ],
        "crypto": [
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1629339942248-45d4b10c8c2f?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1640340434855-6084b1f4901c?w=1080&h=1920&fit=crop&q=80"
        ],
        "motivation": [
            "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1499209974431-9daccece0089?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1519052537078-e6302a4968d4?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1470246973918-29a93221c455?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=1080&h=1920&fit=crop&q=80"
        ],
        "history": [
            "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1539650116574-8efeb43e2750?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1533158307587-828f0a76ef46?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=1080&h=1920&fit=crop&q=80"
        ],
        "nature": [
            "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1505765050516-f72dcac9c60e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518791841217-8f162f1e1131?w=1080&h=1920&fit=crop&q=80"
        ],
        "mind": [
            "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1529699211952-734e80c4d42b?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1517842645767-c639042777db?w=1080&h=1920&fit=crop&q=80"
        ],
        "tech": [
            "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1555680202-c86f0e12f086?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1531482615713-2afd69097998?w=1080&h=1920&fit=crop&q=80"
        ],
        "sport": [
            "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1517649763962-0c623266ddc0?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1517963879433-6fa2b0fc862b?w=1080&h=1920&fit=crop&q=80"
        ],
        "cars": [
            "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?w=1080&h=1920&fit=crop&q=80"
        ],
        "future": [
            "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1516116211227-bbc66542d991?w=1080&h=1920&fit=crop&q=80"
        ],
        "ocean": [
            "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1498855926480-d98e83099315?w=1080&h=1920&fit=crop&q=80"
        ],
        "urban": [
            "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1477959858617-67f30bc75b82?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=1080&h=1920&fit=crop&q=80"
        ]
    }

    def __init__(self, format_key: str = DEFAULT_FORMAT):
        fmt = FORMATS.get(format_key, FORMATS[DEFAULT_FORMAT])
        self.width = fmt["width"]
        self.height = fmt["height"]
        self.format_key = format_key

    def detect_category(self, text: str) -> str:
        """Matndagi so'zlarga qarab 12 ta toifadan birini aniqlaydi."""
        t = text.lower()
        if any(w in t for w in ["koinot", "yulduz", "sayyora", "galaktika", "tuynuk", "mars", "quyosh", "space", "astronom"]):
            return "space"
        elif any(w in t for w in ["ai", "sun'iy", "intellekt", "robot", "neyron", "gemini", "gpt"]):
            return "ai"
        elif any(w in t for w in ["kripto", "bitcoin", "btc", "blokcheyn", "ethereum", "valyuta"]):
            return "crypto"
        elif any(w in t for w in ["kod", "dastur", "kompyuter", "kiber", "texnologiya", "it", "xaker", "smartfon"]):
            return "tech"
        elif any(w in t for w in ["mashina", "avto", "superkar", "bmw", "mercedes", "tezlik", "poyga"]):
            return "cars"
        elif any(w in t for w in ["muvaffaqiyat", "boylik", "pul", "biznes", "moliya", "investitsiya", "daromad", "boy", "millioner", "milliarder", "kapital"]):
            return "business"
        elif any(w in t for w in ["motivatsiya", "iroda", "maqsad", "orzuingiz", "taslim", "g'alaba"]):
            return "motivation"
        elif any(w in t for w in ["sport", "mashq", "fitnes", "kuch", "salomatlik", "intizom", "yugurish"]):
            return "sport"
        elif any(w in t for w in ["tarix", "qadimgi", "piramida", "jumboq", "sivilizatsiya", "arxeolog", "rim", "misr"]):
            return "history"
        elif any(w in t for w in ["miya", "ong", "psixologiya", "fikr", "xotira", "aqlli", "odam", "inson", "tafakkur"]):
            return "mind"
        elif any(w in t for w in ["okean", "dengiz", "akula", "baliq", "suvosti", "coral", "reef", "jellyfish"]):
            return "ocean"
        elif any(w in t for w in ["shahar", "megapolis", "ko'cha", "tokyo", "new york", "london", "metropol", "bino"]):
            return "urban"
        elif any(w in t for w in ["tog'", "tabiat", "o'rmon", "daryo", "hayot", "jonivor", "manzara"]):
            return "nature"
        elif any(w in t for w in ["kelajak", "kiberpank", "sivilizatsiya", "uçuvchi"]):
            return "future"
        return "space"

    def get_music_genre_for_category(self, cat: str) -> str:
        if cat in ["space", "history"]:
            return "cosmic_deep"
        elif cat in ["ai", "crypto", "future"]:
            return "cyber_action"
        elif cat in ["tech"]:
            return "tech_modern"
        elif cat in ["business", "sport", "motivation", "cars"]:
            return "epic_inspiration"
        elif cat in ["mind", "nature"]:
            return "lofi_vibes"
        else:
            return "ambient_chill"

    def process_custom_user_image(self, input_image_path: str, output_path: str) -> str:
        """
        Foydalanuvchi rasmini professional formatga moslash:
        Agar rasm formati boshqacha bo'lsa (masalan 16:9 yoki 1:1), kesib tashlamasdan
        orqa fonga xiralashgan (Blurred Glass Pad) chiroyli fon beradi va markazga joylaydi!
        """
        try:
            with Image.open(input_image_path) as im:
                im_ratio = im.width / im.height
                target_ratio = self.width / self.height

                # Agar rasm video formatiga deyarli mos bo'lsa
                if abs(im_ratio - target_ratio) < 0.12:
                    if im_ratio > target_ratio:
                        new_h = self.height
                        new_w = int(new_h * im_ratio)
                    else:
                        new_w = self.width
                        new_h = int(new_w / im_ratio)
                    resized = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    l = (new_w - self.width) // 2
                    t = (new_h - self.height) // 2
                    cropped = resized.crop((l, t, l + self.width, t + self.height))
                    cropped.save(output_path, "JPEG", quality=95)
                else:
                    # Smart Glassmorphic Blur Pad (Nafis xira orqa fon + markazda to'liq rasm)
                    bg = im.resize((self.width, self.height), Image.Resampling.LANCZOS)
                    bg = bg.filter(ImageFilter.GaussianBlur(55))
                    dim = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 75))
                    bg = Image.alpha_composite(bg.convert("RGBA"), dim)

                    # Foreground fit
                    if im_ratio > target_ratio:
                        fg_w = self.width
                        fg_h = int(self.width / im_ratio)
                    else:
                        fg_h = self.height
                        fg_w = int(self.height * im_ratio)
                    fg = im.resize((fg_w, fg_h), Image.Resampling.LANCZOS)

                    pos_x = (self.width - fg_w) // 2
                    pos_y = (self.height - fg_h) // 2
                    bg.paste(fg, (pos_x, pos_y))
                    bg.convert("RGB").save(output_path, "JPEG", quality=95)

                self._apply_cinematic_grade(output_path)
                return output_path
        except Exception as e:
            print(f"[User Image Process Error] {e}")
            return input_image_path

    def get_scene_visual(
        self,
        prompt: str,
        output_path: str,
        seed: int = None,
        scene_num: int = 1,
        art_style: str = DEFAULT_ART_STYLE
    ) -> str:
        """
        1-Bosqich: Real-Time AI Generation (Pollinations AI Flux)
        2-Bosqich (Failover): Curated 4K Unsplash/Picsum kutubxonasi
        3-Bosqich (Failover): Oflayn kinoviy grafika
        """
        if seed is None:
            seed = random.randint(10000, 999999)

        cat = self.detect_category(prompt)
        style_info = ART_STYLES.get(art_style, ART_STYLES[DEFAULT_ART_STYLE])
        prompt_suffix = style_info.get("prompt_suffix", ", 8k resolution, cinematic lighting, photorealistic, dramatic vertical shot")
        model = style_info.get("model", "")
        model_param = f"&model={model}" if model else ""

        # 1-Urinish: Real-Time Pollinations AI Generator (Birlamchi va Zaxira Mirror)
        ai_success = False
        full_prompt = f"{prompt}{prompt_suffix}"
        encoded_prompt = urllib.parse.quote(full_prompt)

        for p_url in [
            f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={self.width}&height={self.height}&nologo=true&seed={seed}{model_param}",
            f"https://pollinations.ai/p/{encoded_prompt}?width={self.width}&height={self.height}&seed={seed}"
        ]:
            try:
                ai_success = self._download_image(p_url, output_path, timeout=9)
                if ai_success and os.path.exists(output_path) and os.path.getsize(output_path) >= 3000:
                    break
            except Exception:
                ai_success = False

        # 2-Urinish: Kengaytirilgan 130+ Kinematik Fotolar Jamg'armasi (Shablon takrorlanishidan 100% holi)
        if not ai_success or not os.path.exists(output_path) or os.path.getsize(output_path) < 3000:
            curated_urls = self.CURATED_THEMES.get(cat, self.CURATED_THEMES["space"])
            import hashlib
            hash_val = int(hashlib.md5(f"{prompt}_{seed}_{scene_num}_{time.time():.0f}".encode("utf-8")).hexdigest(), 16)
            target_url = curated_urls[hash_val % len(curated_urls)]
            ai_success = self._download_image(target_url, output_path, timeout=8)

        # 3-Urinish: Picsum Dynamic High-Res Seed
        if not ai_success or not os.path.exists(output_path) or os.path.getsize(output_path) < 3000:
            clean_seed = f"cinema_{cat}_{seed}_{scene_num}"
            picsum_url = f"https://picsum.photos/seed/{clean_seed}/{self.width}/{self.height}"
            ai_success = self._download_image(picsum_url, output_path, timeout=8)

        # 4-Urinish: 100% Oflayn badiiy kinoviy grafika
        if not ai_success or not os.path.exists(output_path) or os.path.getsize(output_path) < 3000:
            self._generate_fallback_graphic(cat, output_path)

        self._apply_cinematic_grade(output_path)
        return output_path

    def _download_image(self, url: str, output_path: str, timeout: int = 10) -> bool:
        for attempt in range(2):
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as response, open(output_path, "wb") as out_file:
                    out_file.write(response.read())
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    return True
            except Exception:
                if attempt == 0:
                    time.sleep(0.5)
        return False

    def _generate_fallback_graphic(self, category: str, output_path: str):
        """Oflayn ko'p qatlamli kinoviy grafika generatsiyasi."""
        img = Image.new("RGB", (self.width, self.height), color="#080C16")
        draw = ImageDraw.Draw(img)

        palette_map = {
            "space": ("#040714", "#120926", (0, 190, 255), (255, 0, 140)),
            "ai": ("#020B14", "#091D33", (0, 240, 255), (80, 0, 255)),
            "business": ("#0A0F0D", "#1C2417", (255, 215, 0), (0, 200, 120)),
            "crypto": ("#0B0D17", "#1E1A0A", (255, 180, 0), (0, 230, 255)),
            "motivation": ("#120505", "#2B0B0B", (255, 60, 0), (255, 200, 0)),
            "history": ("#140D07", "#2E1C0F", (230, 160, 80), (180, 120, 50)),
            "sport": ("#120505", "#2B0B0B", (255, 60, 0), (255, 200, 0)),
            "tech": ("#030914", "#08182B", (0, 150, 255), (0, 255, 180)),
            "cars": ("#110508", "#240915", (255, 40, 80), (200, 200, 255)),
            "mind": ("#090717", "#181136", (180, 100, 255), (0, 200, 255)),
            "nature": ("#03120A", "#0C2E1A", (0, 230, 110), (0, 180, 220)),
            "ocean": ("#010C17", "#032038", (0, 160, 255), (0, 255, 220)),
            "urban": ("#0B0714", "#19112B", (255, 0, 120), (255, 220, 0)),
            "future": ("#020E1A", "#08243D", (0, 255, 230), (255, 0, 180))
        }
        bg1, bg2, glow1, glow2 = palette_map.get(category, palette_map["space"])

        for y in range(self.height):
            ratio = y / self.height
            r = int(int(bg1[1:3], 16) * (1 - ratio) + int(bg2[1:3], 16) * ratio)
            g = int(int(bg1[3:5], 16) * (1 - ratio) + int(bg2[3:5], 16) * ratio)
            b = int(int(bg1[5:7], 16) * (1 - ratio) + int(bg2[5:7], 16) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        d_overlay = ImageDraw.Draw(overlay)

        d_overlay.ellipse(
            [self.width * 0.1, self.height * 0.22, self.width * 0.9, self.height * 0.65],
            fill=(glow1[0], glow1[1], glow1[2], 50)
        )
        d_overlay.ellipse(
            [self.width * 0.2, self.height * 0.45, self.width * 0.8, self.height * 0.85],
            fill=(glow2[0], glow2[1], glow2[2], 40)
        )
        overlay = overlay.filter(ImageFilter.GaussianBlur(110))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        draw_stars = ImageDraw.Draw(img)
        for _ in range(120):
            sx = random.randint(0, self.width)
            sy = random.randint(0, self.height)
            b_val = random.randint(190, 255)
            draw_stars.point((sx, sy), fill=(b_val, b_val, b_val))

        img.save(output_path, "JPEG", quality=95)

    def _apply_cinematic_grade(self, image_path: str):
        """Kinoviy vinyetka va rang kontrast qo'shish."""
        try:
            with Image.open(image_path) as im:
                im_ratio = im.width / im.height
                target_ratio = self.width / self.height

                if im_ratio > target_ratio:
                    new_height = self.height
                    new_width = int(new_height * im_ratio)
                else:
                    new_width = self.width
                    new_height = int(new_width / im_ratio)

                resized = im.resize((new_width, new_height), Image.Resampling.LANCZOS)
                left = (new_width - self.width) // 2
                top = (new_height - self.height) // 2
                cropped = resized.crop((left, top, left + self.width, top + self.height))

                vignette = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
                draw_v = ImageDraw.Draw(vignette)
                draw_v.rectangle([0, 0, self.width, self.height], fill=(0, 0, 0, 35))
                draw_v.ellipse([self.width * 0.05, self.height * 0.1, self.width * 0.95, self.height * 0.9], fill=(0, 0, 0, 0))
                vignette = vignette.filter(ImageFilter.GaussianBlur(80))

                composited = Image.alpha_composite(cropped.convert("RGBA"), vignette).convert("RGB")

                enhancer = ImageEnhance.Sharpness(composited)
                sharpened = enhancer.enhance(1.22)
                enhancer_c = ImageEnhance.Contrast(sharpened)
                final_img = enhancer_c.enhance(1.06)

                final_img.save(image_path, "JPEG", quality=95)
        except Exception as e:
            print(f"[Cinematic Grade Error] {e}")

    def generate_thumbnail_card(self, image_path: str, title: str, output_thumb_path: str) -> str:
        """Telegram video kartochkasi uchun ixcham, yuqori sifatli muqova (thumbnail) yaratish."""
        try:
            with Image.open(image_path) as im:
                thumb_w = 320 if self.width < self.height else 640
                thumb_h = int(thumb_w * (self.height / self.width))
                resized = im.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                resized.save(output_thumb_path, "JPEG", quality=90)
                return output_thumb_path
        except Exception as e:
            print(f"[Thumbnail Generate Error] {e}")
            return image_path

    def generate_cover_poster(self, image_path: str, title: str, output_poster_path: str) -> str:
        """
        YouTube Shorts, TikTok va Reels uchun 1080x1920 Full HD dizaynerlik muqova posteri (Cover Poster).
        """
        try:
            with Image.open(image_path) as im:
                base = im.convert("RGBA").resize((self.width, self.height), Image.Resampling.LANCZOS)
                overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
                draw = ImageDraw.Draw(overlay)

                # Yuqori va pastki qismda kinolarga xos mayin qorayish (cinematic gradient/vignette)
                draw.rectangle([(0, 0), (self.width, int(self.height * 0.16))], fill=(0, 0, 0, 140))
                draw.rectangle([(0, int(self.height * 0.82)), (self.width, self.height)], fill=(0, 0, 0, 180))

                # Yuqori brending badge
                draw.rectangle(
                    [(30, 40), (self.width - 30, 110)],
                    fill=(10, 15, 30, 200),
                    outline=(0, 255, 255, 220),
                    width=2
                )
                draw.text((50, 60), "MuzaffarZed AI Studios • Official Cover", fill=(255, 255, 255, 240))

                # Pastki mualliflik muhri
                draw.rectangle(
                    [(30, self.height - 100), (self.width - 30, self.height - 40)],
                    fill=(10, 15, 30, 200),
                    outline=(255, 215, 0, 220),
                    width=2
                )
                draw.text((50, self.height - 80), "Dasturchi: MuzaffarZed", fill=(255, 215, 0, 240))

                composited = Image.alpha_composite(base, overlay).convert("RGB")
                composited.save(output_poster_path, "JPEG", quality=95)
                return output_poster_path
        except Exception as e:
            print(f"[Cover Poster Error] {e}")
            return image_path
