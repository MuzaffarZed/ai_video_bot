"""
MuzaffarZed AI Video Bot - Zamonaviy Karaoke Subtitrlar Generatori (Version 7.0 Singularity Glassmorphic)
Ko'p formatli (9:16, 16:9, 1:1), 4 xil rang, shishasimon soya (Glassmorphic Shadow) va 120% pop.
Muallif: MuzaffarZed
"""
import os
import sys
from typing import List, Dict
from config import (
    WATERMARK_TEXT,
    FORMATS,
    DEFAULT_FORMAT,
    SUBTITLE_THEMES,
    DEFAULT_SUBTITLE_THEME,
    SUBTITLE_SIZES,
    DEFAULT_SUBTITLE_SIZE
)

class SubtitleEngine:
    def __init__(self, font_name: str = None):
        if font_name is None:
            self.font_name = "DejaVu Sans" if sys.platform != "win32" else "Arial"
        else:
            self.font_name = font_name

    @staticmethod
    def _format_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        centi = int((secs - int(secs)) * 100)
        return f"{hours}:{minutes:02d}:{int(secs):02d}.{centi:02d}"

    def generate_ass(
        self,
        scenes: List[Dict],
        output_ass_path: str,
        theme_key: str = DEFAULT_SUBTITLE_THEME,
        format_key: str = DEFAULT_FORMAT,
        size_key: str = DEFAULT_SUBTITLE_SIZE
    ) -> str:
        watermark_font = "DejaVu Sans" if sys.platform != "win32" else "Segoe UI"
        
        fmt = FORMATS.get(format_key, FORMATS[DEFAULT_FORMAT])
        play_x = fmt["width"]
        play_y = fmt["height"]
        margin_v = fmt.get("safe_margin_v", 480)

        theme_data = SUBTITLE_THEMES.get(theme_key, SUBTITLE_THEMES[DEFAULT_SUBTITLE_THEME])
        active_bgr = theme_data["active_color"]
        base_bgr = theme_data["base_color"]
        outline_bgr = theme_data["outline_color"]

        base_size = SUBTITLE_SIZES.get(size_key, SUBTITLE_SIZES[DEFAULT_SUBTITLE_SIZE])["size"]
        actual_font_size = base_size if format_key != "16:9" else int(base_size * 0.82)

        # Qora shishasimon soya (Shadow=4, Outline=6) har qanday fonda 100% o'qilishni kafolatlaydi
        ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_x}
PlayResY: {play_y}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,{self.font_name},{actual_font_size},{base_bgr},{active_bgr},{outline_bgr},&H95000000,-1,0,0,0,100,100,1,0,1,6,4,2,60,60,{margin_v},1
Style: Watermark,{watermark_font},34,&H75FFFFFF,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,9,40,40,75,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []

        total_duration = scenes[-1]["end_time"] if scenes else 10.0
        start_str_full = self._format_time(0.0)
        end_str_full = self._format_time(total_duration)

        events.append(f"Dialogue: 1,{start_str_full},{end_str_full},Watermark,,0,0,0,,{WATERMARK_TEXT}")

        emojis = ["🔥", "💡", "🧠", "✨", "🚀", "⚡", "🎯", "💎", "⏳", "👑"]

        for sc_idx, sc in enumerate(scenes):
            words = sc.get("words", [])
            if not words:
                continue

            scene_emoji = emojis[sc_idx % len(emojis)]
            spk = sc.get("speaker", 1)
            # Speaker 2 uchun kontrast rang (Neon pushti-binafsha)
            cur_active_bgr = "&H00FF60D0" if spk == 2 else active_bgr
            speaker_badge = "👩 " if spk == 2 else ("👨 " if "speaker" in sc else "")

            chunk_size = 3
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i + chunk_size]

                for active_idx, w in enumerate(chunk):
                    w_start = w["start"]
                    w_end = w["end"]

                    line_parts = []
                    if i == 0:
                        line_parts.append(f"{speaker_badge}{scene_emoji}")

                    for idx, part in enumerate(chunk):
                        word_text = part["word"]
                        if idx == active_idx:
                            # 120% pop va neon yonuvchi rang
                            line_parts.append(f"{{\\c{cur_active_bgr}&\\fscx120\\fscy120}}{word_text}{{\\rKaraoke}}")
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

    def generate_srt(self, scenes: List[Dict], output_srt_path: str) -> str:
        """CapCut, Adobe Premiere va YouTube uchun standart SRT subtitr fayli yaratish."""
        entries = []
        counter = 1
        for sc in scenes:
            spk = sc.get("speaker", 1)
            spk_prefix = f"[Speaker {spk}] " if "speaker" in sc else ""
            words = sc.get("words", [])
            chunk_size = 4
            for i in range(0, len(words), chunk_size):
                chunk = words[i:i + chunk_size]
                if not chunk:
                    continue
                start_time = self._format_srt_time(chunk[0]["start"])
                end_time = self._format_srt_time(chunk[-1]["end"])
                chunk_text = " ".join([w["word"] for w in chunk])
                entries.append(f"{counter}\n{start_time} --> {end_time}\n{spk_prefix}{chunk_text}\n")
                counter += 1

        with open(output_srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(entries))
        return output_srt_path

    @staticmethod
    def _format_srt_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int(round((seconds - int(seconds)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
