"""
MuzaffarZed AI Video Bot - Kengaytirilgan Vizual Kadrlar Dvigateli (Visual Studio 8.0 Grandmaster)
Haqiqiy Real-Time AI rasm generatsiyasi (Pollinations Flux AI), 12 toifali 4K kutubxona va fotorealistik filtr.
Muallif: MuzaffarZed
"""
import os
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
            "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1080&h=1920&fit=crop&q=80"
        ],
        "ai": [
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507146426996-ef05306b995a?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1080&h=1920&fit=crop&q=80"
        ],
        "business": [
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1579532537598-459ecdaf39cc?w=1080&h=1920&fit=crop&q=80"
        ],
        "crypto": [
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=1080&h=1920&fit=crop&q=80"
        ],
        "motivation": [
            "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1499209974431-9daccece0089?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=1080&h=1920&fit=crop&q=80"
        ],
        "history": [
            "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=1080&h=1920&fit=crop&q=80"
        ],
        "nature": [
            "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=1080&h=1920&fit=crop&q=80"
        ],
        "mind": [
            "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1080&h=1920&fit=crop&q=80"
        ],
        "tech": [
            "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1080&h=1920&fit=crop&q=80"
        ],
        "sport": [
            "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1080&h=1920&fit=crop&q=80"
        ],
        "cars": [
            "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=1080&h=1920&fit=crop&q=80"
        ],
        "future": [
            "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080&h=1920&fit=crop&q=80"
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
        elif any(w in t for w in ["dengiz", "okean", "tog'", "tabiat", "suv", "o'rmon", "hayot", "jonivor"]):
            return "nature"
        elif any(w in t for w in ["kelajak", "kiberpank", "shahar", "sivilizatsiya"]):
            return "future"
        return "space"

    def get_music_genre_for_category(self, cat: str) -> str:
        if cat in ["space", "history"]:
            return "cosmic_deep"
        elif cat in ["ai", "tech", "crypto", "future"]:
            return "tech_modern"
        elif cat in ["business", "sport", "motivation", "cars"]:
            return "epic_inspiration"
        else:
            return "ambient_chill"

    def process_custom_user_image(self, input_image_path: str, output_path: str) -> str:
        """Foydalanuvchi yuborgan rasmni video formatiga moslab qayta ishlash."""
        try:
            with Image.open(input_image_path) as im:
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

                cropped.save(output_path, "JPEG", quality=95)
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
        model = style_info.get("model", "flux-realism")

        # 1-Urinish: Real-Time Pollinations AI Generator
        ai_success = False
        try:
            full_prompt = f"{prompt}{prompt_suffix}"
            encoded_prompt = urllib.parse.quote(full_prompt)
            pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={self.width}&height={self.height}&nologo=true&seed={seed}&model={model}"
            ai_success = self._download_image(pollinations_url, output_path, timeout=9)
        except Exception as e:
            ai_success = False

        # 2-Urinish: Curated 4K fotolar bazasi
        if not ai_success or not os.path.exists(output_path) or os.path.getsize(output_path) < 3000:
            curated_urls = self.CURATED_THEMES.get(cat, self.CURATED_THEMES["space"])
            target_url = curated_urls[(scene_num - 1 + seed) % len(curated_urls)]
            ai_success = self._download_image(target_url, output_path, timeout=10)

        # 3-Urinish: Picsum Seed
        if not ai_success or not os.path.exists(output_path) or os.path.getsize(output_path) < 3000:
            clean_seed = f"v_{cat}_{seed}_{scene_num}"
            picsum_url = f"https://picsum.photos/seed/{clean_seed}/{self.width}/{self.height}"
            ai_success = self._download_image(picsum_url, output_path, timeout=10)

        # 4-Urinish: 100% Oflayn badiiy grafika
        if not ai_success or not os.path.exists(output_path) or os.path.getsize(output_path) < 3000:
            self._generate_fallback_graphic(cat, output_path)

        self._apply_cinematic_grade(output_path)
        return output_path

    def _download_image(self, url: str, output_path: str, timeout: int = 10) -> bool:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response, open(output_path, "wb") as out_file:
                out_file.write(response.read())
            return True
        except Exception:
            return False

    def _generate_fallback_graphic(self, category: str, output_path: str):
        """Oflayn ko'p qatlamli kinoviy grafika generatsiyasi."""
        img = Image.new("RGB", (self.width, self.height), color="#080C16")
        draw = ImageDraw.Draw(img)

        palette_map = {
            "space": ("#040714", "#120926", (0, 190, 255), (255, 0, 140)),
            "ai": ("#020B14", "#091D33", (0, 240, 255), (80, 0, 255)),
            "business": ("#0A0F0D", "#1C2417", (255, 215, 0), (0, 200, 120)),
            "motivation": ("#120505", "#2B0B0B", (255, 60, 0), (255, 200, 0)),
            "sport": ("#120505", "#2B0B0B", (255, 60, 0), (255, 200, 0)),
            "tech": ("#030914", "#08182B", (0, 150, 255), (0, 255, 180)),
            "nature": ("#03120A", "#0C2E1A", (0, 230, 110), (0, 180, 220))
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
