"""
MuzaffarZed AI Video Bot - Kengaytirilgan Vizual Kadrlar Dvigateli (Visual Studio 2.0)
Mavzuga mos tematik 1080x1920 4K fotosuratlar, Pixabay/Unsplash integratsiyasi va oflayn grafika.
Muallif: MuzaffarZed
"""
import os
import random
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageFilter
from config import TEMP_DIR

class VisualEngine:
    # Mavzular bo'yicha saralangan eng yuqori sifatli 1080x1920 vertikal fotolar bazasi
    CURATED_THEMES = {
        "space": [
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1447433819943-74a20887a81e?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=1080&h=1920&fit=crop&q=80"
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
        "history": [
            "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1533158307587-828f0a76ef46?w=1080&h=1920&fit=crop&q=80"
        ],
        "nature": [
            "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1080&h=1920&fit=crop&q=80"
        ],
        "mind": [
            "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1080&h=1920&fit=crop&q=80",
            "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1080&h=1920&fit=crop&q=80"
        ]
    }

    def __init__(self, target_width: int = 1080, target_height: int = 1920):
        self.width = target_width
        self.height = target_height

    def detect_category(self, text: str) -> str:
        """
        Matndagi so'zlarga qarab mavzu toifasini aniqlaydi.
        """
        t = text.lower()
        if any(w in t for w in ["koinot", "yulduz", "sayyora", "galaktika", "tuynuk", "mars", "quyosh", "space", "astronom"]):
            return "space"
        elif any(w in t for w in ["ai", "sun'iy", "intellekt", "robot", "kelajak", "texnologiya", "dastur", "kod", "kompyuter", "kiber"]):
            return "ai"
        elif any(w in t for w in ["muvaffaqiyat", "boylik", "pul", "biznes", "moliya", "investitsiya", "maqsad", "boy"]):
            return "business"
        elif any(w in t for w in ["tarix", "qadimgi", "piramida", "jumboq", "sivilizatsiya", "arxeolog", "rim", "misr"]):
            return "history"
        elif any(w in t for w in ["miya", "ong", "psixologiya", "fikr", "xotira", "aqlli", "odam", "inson"]):
            return "mind"
        elif any(w in t for w in ["dengiz", "okean", "tog'", "tabiat", "suv", "o'rmon", "hayot", "jonivor"]):
            return "nature"
        return "space"

    def get_scene_visual(self, prompt: str, output_path: str, seed: int = None, scene_num: int = 1) -> str:
        """
        Kadr uchun mavzuga 100% mos 1080x1920 sifatli kadrni yuklaydi yoki chizadi.
        """
        if seed is None:
            seed = random.randint(10000, 999999)

        cat = self.detect_category(prompt)
        curated_urls = self.CURATED_THEMES.get(cat, self.CURATED_THEMES["space"])
        
        # Har bir kadr uchun har xil rasm tanlash
        target_url = curated_urls[(scene_num - 1 + seed) % len(curated_urls)]

        success = self._download_image(target_url, output_path)
        if not success or not os.path.exists(output_path) or os.path.getsize(output_path) < 2000:
            # Zaxira: Picsum seeded URL
            clean_seed = f"v_{cat}_{seed}_{scene_num}"
            picsum_url = f"https://picsum.photos/seed/{clean_seed}/{self.width}/{self.height}"
            success = self._download_image(picsum_url, output_path)

        if not success or not os.path.exists(output_path) or os.path.getsize(output_path) < 2000:
            # 3-bosqich: To'liq oflayn estetik grafika
            self._generate_fallback_graphic(prompt, output_path)

        self._ensure_exact_dimensions(output_path)
        return output_path

    def _download_image(self, url: str, output_path: str) -> bool:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=10) as response, open(output_path, "wb") as out_file:
                out_file.write(response.read())
            return True
        except Exception as e:
            print(f"[Visual Download] {e}")
            return False

    def _generate_fallback_graphic(self, prompt: str, output_path: str):
        """
        Oflayn kosmik va tumanlik fon generatsiyasi.
        """
        img = Image.new("RGB", (self.width, self.height), color="#080C16")
        draw = ImageDraw.Draw(img)

        palettes = [
            ("#050811", "#150D2A"),
            ("#030A1A", "#0A1F3D"),
            ("#0F0024", "#00102B")
        ]
        c1, c2 = random.choice(palettes)

        for y in range(self.height):
            ratio = y / self.height
            r = int(int(c1[1:3], 16) * (1 - ratio) + int(c2[1:3], 16) * ratio)
            g = int(int(c1[3:5], 16) * (1 - ratio) + int(c2[3:5], 16) * ratio)
            b = int(int(c1[5:7], 16) * (1 - ratio) + int(c2[5:7], 16) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        d_overlay = ImageDraw.Draw(overlay)

        d_overlay.ellipse(
            [self.width * 0.1, self.height * 0.25, self.width * 0.9, self.height * 0.65],
            fill=(0, 190, 255, 40)
        )
        d_overlay.ellipse(
            [self.width * 0.2, self.height * 0.45, self.width * 0.8, self.height * 0.85],
            fill=(255, 0, 140, 30)
        )
        overlay = overlay.filter(ImageFilter.GaussianBlur(100))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        draw_stars = ImageDraw.Draw(img)
        for _ in range(90):
            sx = random.randint(0, self.width)
            sy = random.randint(0, self.height)
            b_val = random.randint(180, 255)
            draw_stars.point((sx, sy), fill=(b_val, b_val, b_val))

        img.save(output_path, "JPEG", quality=95)

    def _ensure_exact_dimensions(self, image_path: str):
        try:
            with Image.open(image_path) as im:
                if im.size != (self.width, self.height):
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
                    cropped.save(image_path, "JPEG", quality=95)
        except Exception as e:
            print(f"[Visual Dimension Error] {e}")
