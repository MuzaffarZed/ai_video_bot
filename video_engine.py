"""
MuzaffarZed AI Video Bot - Kengaytirilgan Video Montaj Dvigateli (Version 6.0 Zenith Visual Filters)
Ko'p formatli (9:16, 16:9, 1:1), Kinematografik LUT filtrlar (Teal & Orange, Cyberpunk, Golden) va Outro.
Muallif: MuzaffarZed
"""
import os
import subprocess
from typing import List, Dict
from config import (
    BASE_DIR,
    TEMP_DIR,
    OUTPUT_DIR,
    FPS,
    FORMATS,
    DEFAULT_FORMAT,
    SUBTITLE_THEMES,
    DEFAULT_SUBTITLE_THEME,
    VISUAL_FILTERS,
    DEFAULT_VISUAL_FILTER,
    BRAND_NAME,
    WATERMARK_TEXT
)

class VideoEngine:
    def __init__(self, fps: int = FPS):
        self.fps = fps

    def render_scene_clip(
        self,
        image_path: str,
        duration: float,
        output_clip_path: str,
        scene_idx: int = 1,
        format_key: str = DEFAULT_FORMAT,
        filter_key: str = DEFAULT_VISUAL_FILTER
    ) -> str:
        """
        Bitta rasmdan kinematografik suzuvchi kamera harakati (Dynamic Zoom & Pan)
        va tanlangan rang filtri (LUT) bilan Full HD klip hosil qiladi.
        """
        fmt = FORMATS.get(format_key, FORMATS[DEFAULT_FORMAT])
        target_w = fmt["width"]
        target_h = fmt["height"]

        clean_img = os.path.relpath(image_path, BASE_DIR).replace("\\", "/")
        clean_out = os.path.relpath(output_clip_path, BASE_DIR).replace("\\", "/")

        scaled_w = int(target_w * 1.15)
        scaled_h = int(target_h * 1.15)

        if scene_idx % 2 == 1:
            drift_x = f"(in_w-out_w)/2 + sin(t*1.1)*{int(target_w * 0.035)}"
            drift_y = f"(in_h-out_h)/2 + (t/10)*{int(target_h * 0.015)}"
        else:
            drift_x = f"(in_w-out_w)/2 - sin(t*1.1)*{int(target_w * 0.035)}"
            drift_y = f"(in_h-out_h)/2 - (t/10)*{int(target_h * 0.012)}"

        filter_data = VISUAL_FILTERS.get(filter_key, VISUAL_FILTERS[DEFAULT_VISUAL_FILTER])
        color_filter = filter_data.get("filter", "eq=contrast=1.06:saturation=1.14")

        vf_filter = (
            f"scale={scaled_w}:{scaled_h}:force_original_aspect_ratio=increase,crop={scaled_w}:{scaled_h},"
            f"crop={target_w}:{target_h}:x='{drift_x}':y='{drift_y}',"
            f"{color_filter},"
            f"setsar=1"
        )

        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-loop", "1",
            "-t", f"{duration:.3f}",
            "-i", clean_img,
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-threads", "2",
            "-pix_fmt", "yuv420p",
            "-r", str(self.fps),
            clean_out
        ]

        subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, check=True, timeout=60)
        return output_clip_path

    def assemble_final_video(
        self,
        scene_clips: List[str],
        master_audio_path: str,
        ass_subtitle_path: str,
        output_final_path: str,
        total_duration: float = 20.0,
        theme_key: str = DEFAULT_SUBTITLE_THEME,
        format_key: str = DEFAULT_FORMAT
    ) -> str:
        """
        Barcha kadr kliplarini birlashtiradi, ovozni ulaydi,
        zamonaviy progress-barni chizadi va karaoke subtitrni yondiradi.
        """
        concat_txt = TEMP_DIR / "clips_concat.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for clip in scene_clips:
                clean_path = os.path.abspath(clip).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        rel_concat = os.path.abspath(str(concat_txt)).replace("\\", "/")
        rel_audio = os.path.abspath(master_audio_path).replace("\\", "/")
        rel_ass = os.path.relpath(ass_subtitle_path, BASE_DIR).replace("\\", "/") if ass_subtitle_path else ""
        rel_final = os.path.abspath(output_final_path).replace("\\", "/")

        bar_colors = {
            "gold": "0xFFD700@0.95",
            "emerald": "0x00FF7F@0.95",
            "fire": "0xFF3030@0.95",
            "cyan": "0x00FFFF@0.95"
        }
        active_color = bar_colors.get(theme_key, "0xFFD700@0.95")

        dark_rail = "drawbox=x=0:y=ih-14:w=iw:h=14:color=black@0.45:t=fill"
        active_bar = f"drawbox=x=0:y=ih-14:w='iw*(t/{max(1.0, total_duration):.3f})':h=14:color={active_color}:t=fill"
        progress_filter = f"{dark_rail},{active_bar}"

        if rel_ass and os.path.exists(ass_subtitle_path):
            full_vf = f"{progress_filter},ass={rel_ass}"
        else:
            full_vf = progress_filter

        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-f", "concat", "-safe", "0",
            "-i", rel_concat,
            "-i", rel_audio,
            "-vf", full_vf,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-threads", "2",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            rel_final
        ]

        try:
            res = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True, timeout=120)
            if res.returncode == 0 and os.path.exists(output_final_path) and os.path.getsize(output_final_path) > 1000:
                return output_final_path
            print(f"[VideoEngine Notice] Render xatosi: {res.stderr[:200]}")
        except Exception as e:
            print(f"[VideoEngine Notice] Render sinovi: {e}")

        # Fallback
        cmd_fb = [
            "ffmpeg", "-nostdin", "-y",
            "-f", "concat", "-safe", "0",
            "-i", rel_concat,
            "-i", rel_audio,
            "-vf", progress_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-threads", "2",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            rel_final
        ]
        subprocess.run(cmd_fb, cwd=str(BASE_DIR), capture_output=True, check=True, timeout=120)
        return output_final_path
