"""
MuzaffarZed AI Video Bot - Zamonaviy Karaoke Subtitrlar Generatori (Version 3.0 Multi-Theme)
Alex Hormozi 2.0 dinamik pop karaoke, 4 xil rang sxemasi, xavfsiz zona va mualliflik muhri.
Muallif: MuzaffarZed
"""
import os
import sys
from typing import List, Dict
from config import WATERMARK_TEXT, SUBTITLE_SAFE_MARGIN_V, SUBTITLE_THEMES, DEFAULT_SUBTITLE_THEME

class SubtitleEngine:
    def __init__(self, font_name: str = None, font_size: int = 76):
        if font_name is None:
            self.font_name = "DejaVu Sans" if sys.platform != "win32" else "Arial"
        else:
            self.font_name = font_name
        self.font_size = font_size

    @staticmethod
    def _format_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        centi = int((secs - int(secs)) * 100)
        return f"{hours}:{minutes:02d}:{int(secs):02d}.{centi:02d}"

    def generate_ass(self, scenes: List[Dict], output_ass_path: str, theme_key: str = DEFAULT_SUBTITLE_THEME) -> str:
        """
        Barcha kadrlar so'zlarini tanlangan rang sxemasi bilan zamonaviy ASS formatiga yozadi.
        """
        watermark_font = "DejaVu Sans" if sys.platform != "win32" else "Segoe UI"
        margin_v = SUBTITLE_SAFE_MARGIN_V

        theme_data = SUBTITLE_THEMES.get(theme_key, SUBTITLE_THEMES[DEFAULT_SUBTITLE_THEME])
        active_bgr = theme_data["active_color"]
        base_bgr = theme_data["base_color"]
        outline_bgr = theme_data["outline_color"]

        ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,{self.font_name},{self.font_size},{base_bgr},{active_bgr},{outline_bgr},&H80000000,-1,0,0,0,100,100,1,0,1,6,3,2,60,60,{margin_v},1
Style: Watermark,{watermark_font},34,&H75FFFFFF,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,9,40,40,75,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []

        total_duration = scenes[-1]["end_time"] if scenes else 10.0
        start_str_full = self._format_time(0.0)
        end_str_full = self._format_time(total_duration)

        # 1. Doimiy nafis mualliflik muhri (Dasturchi: MuzaffarZed)
        events.append(f"Dialogue: 1,{start_str_full},{end_str_full},Watermark,,0,0,0,,{WATERMARK_TEXT}")

        emojis = ["🔥", "💡", "🧠", "✨", "🚀", "⚡", "🎯", "💎", "⏳", "👑"]

        # 2. Hormozi 2-3 so'zli dinamik pop karaoke
        for sc_idx, sc in enumerate(scenes):
            words = sc.get("words", [])
            if not words:
                continue

            scene_emoji = emojis[sc_idx % len(emojis)]
            chunk_size = 3  # Mobil ekran uchun optimal 2-3 so'z
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i + chunk_size]

                for active_idx, w in enumerate(chunk):
                    w_start = w["start"]
                    w_end = w["end"]

                    line_parts = []
                    if active_idx == 0 and i == 0:
                        line_parts.append(f"{scene_emoji}")

                    for idx, part in enumerate(chunk):
                        word_text = part["word"]
                        if idx == active_idx:
                            # Tanlangan mavzu rangida yonish va 118% pop kattalashuv
                            line_parts.append(f"{{\\c{active_bgr}&\\fscx118\\fscy118}}{word_text}{{\\rKaraoke}}")
                        else:
                            line_parts.append(f"{{\\c{base_bgr}&}}{word_text}")
                    
                    dialogue_text = " ".join(line_parts)
                    ev_start = self._format_time(w_start)
                    ev_end = self._format_time(w_end)
                    events.append(f"Dialogue: 0,{ev_start},{ev_end},Karaoke,,0,0,0,,{dialogue_text}")

        full_content = ass_header + "\n".join(events) + "\n"

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(full_content)

        return output_ass_path
