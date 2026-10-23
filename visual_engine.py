"""
MuzaffarZed AI Video Bot - Vizual Kadrlar Generatori
Full HD 1080x1920 vertikal sifatli kadrlar va oflayn estetik grafika.
Muallif: MuzaffarZed
"""
import os
import random
import urllib.request
import urllib.parse
from PIL import Image, ImageDraw, ImageFilter
from config import TEMP_DIR

class VisualEngine:
    def __init__(self, target_width: int = 1080, target_height: int = 1920):
        self.width = target_width
        self.height = target_height

    def get_scene_visual(self, prompt: str, output_path: str, seed: int = None) -> str:
        """
        Kadr uchun vizual tasvir yuklaydi yoki chizadi.
        """
        if seed is None:
            seed = random.randint(10000, 999999)

        success = self._download_online_image(prompt, output_path, seed)
        if not success or not os.path.exists(output_path) or os.path.getsize(output_path) < 2000:
            print(f"[Visual Engine] Oflayn estetik kadr generatsiya qilinmoqda: {output_path}")
            self._generate_fallback_graphic(prompt, output_path)

        # O'lchamni aniq 1080x1920 ga moslashtirish
        self._ensure_exact_dimensions(output_path)
        return output_path

    def _download_online_image(self, prompt: str, output_path: str, seed: int) -> bool:
        """
        Yuqori aniqlikdagi 1080x1920 Full HD tasvirni bepul manbadan yuklaydi.
        """
        clean_seed = f"v_{seed}_{abs(hash(prompt)) % 100000}"
        url = f"https://picsum.photos/seed/{clean_seed}/{self.width}/{self.height}"
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=12) as response, open(output_path, "wb") as out_file:
                out_file.write(response.read())
            return True
        except Exception as e:
            print(f"[Visual Download Notice] {e}")
            return False

    def _generate_fallback_graphic(self, prompt: str, output_path: str):
        """
        To'liq oflayn, nafis kosmik va neon uslubidagi gradient fon.
        """
        img = Image.new("RGB", (self.width, self.height), color="#0A0E1A")
        draw = ImageDraw.Draw(img)

        # Gradient palitralari
        palettes = [
            ("#090A0F", "#1A102F"),
            ("#050C1A", "#0B2545"),
            ("#12002B", "#001233"),
            ("#03071E", "#370617")
        ]
        c1, c2 = random.choice(palettes)

        for y in range(self.height):
            ratio = y / self.height
            r = int(int(c1[1:3], 16) * (1 - ratio) + int(c2[1:3], 16) * ratio)
            g = int(int(c1[3:5], 16) * (1 - ratio) + int(c2[3:5], 16) * ratio)
            b = int(int(c1[5:7], 16) * (1 - ratio) + int(c2[5:7], 16) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))

        # Yengil yulduzlar va nurli tumanlik effekti
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        d_overlay = ImageDraw.Draw(overlay)

        # Tumanlik nurlari
        d_overlay.ellipse(
            [self.width * 0.1, self.height * 0.25, self.width * 0.9, self.height * 0.65],
            fill=(0, 180, 255, 35)
        )
        d_overlay.ellipse(
            [self.width * 0.2, self.height * 0.45, self.width * 0.8, self.height * 0.85],
            fill=(255, 0, 128, 25)
        )
        overlay = overlay.filter(ImageFilter.GaussianBlur(100))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

        # Mayda yulduzlar nuqtalari
        draw_stars = ImageDraw.Draw(img)
        for _ in range(80):
            sx = random.randint(0, self.width)
            sy = random.randint(0, self.height)
            brightness = random.randint(180, 255)
            draw_stars.point((sx, sy), fill=(brightness, brightness, brightness))

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
