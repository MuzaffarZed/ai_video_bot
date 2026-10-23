"""
MuzaffarZed AI Video Bot - Kengaytirilgan Video Montaj Dvigateli (Version 2.0)
Kinematografik kamera harakati (Camera Drift), dinamik progress-bar, to'yingan ranglar va karaoke.
Muallif: MuzaffarZed
"""
import os
import subprocess
from typing import List, Dict
from config import BASE_DIR, TEMP_DIR, OUTPUT_DIR, FPS

class VideoEngine:
    def __init__(self, fps: int = FPS):
        self.fps = fps

    def render_scene_clip(self, image_path: str, duration: float, output_clip_path: str, scene_idx: int = 1) -> str:
        """
        Bitta rasmdan kinematografik suzuvchi kamera harakati va to'yingan ranglarga ega
        Full HD (1080x1920) dinamik klip hosil qiladi.
        """
        clean_img = os.path.relpath(image_path, BASE_DIR).replace("\\", "/")
        clean_out = os.path.relpath(output_clip_path, BASE_DIR).replace("\\", "/")

        # Kadr indeksiga qarab harakat yo'nalishini o'zgartirish (dinamika uchun)
        if scene_idx % 2 == 1:
            # 1 va 3-kadrlar: Yengil o'ngga va pastga suzish
            drift_x = "(in_w-out_w)/2 + sin(t*1.2)*35"
            drift_y = "(in_h-out_h)/2 + cos(t*1.0)*25"
        else:
            # 2 va 4-kadrlar: Yengil chapga va yuqoriga suzish
            drift_x = "(in_w-out_w)/2 - sin(t*1.1)*35"
            drift_y = "(in_h-out_h)/2 - cos(t*0.9)*25"

        # 1200x2133 masshtabdan 1080x1920 ga silliq suzuvchi crop + kinematografik rang kontrast
        vf_filter = (
            f"scale=1200:2133:force_original_aspect_ratio=increase,crop=1200:2133,"
            f"crop=1080:1920:x='{drift_x}':y='{drift_y}',"
            f"eq=contrast=1.06:saturation=1.14,"
            f"setsar=1"
        )

        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-loop", "1",
            "-t", f"{duration:.3f}",
            "-i", clean_img,
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "ultrafast",
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
        total_duration: float = 20.0
    ) -> str:
        """
        Barcha kadr kliplarini birlashtiradi, ovozni ulaydi,
        zamonaviy oltin progress-barni chizadi va karaoke subtitrni yondiradi.
        """
        concat_txt = TEMP_DIR / "clips_concat.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for clip in scene_clips:
                clean_path = os.path.abspath(clip).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        rel_concat = os.path.abspath(str(concat_txt)).replace("\\", "/")
        rel_audio = os.path.abspath(master_audio_path).replace("\\", "/")
        rel_ass = os.path.relpath(ass_subtitle_path, BASE_DIR).replace("\\", "/")
        rel_final = os.path.abspath(output_final_path).replace("\\", "/")

        # Pastki qismdagi zamonaviy progress chizig'i filtri (Qorong'i rels + Oltin chiziq)
        dark_rail = "drawbox=x=0:y=ih-14:w=iw:h=14:color=black@0.45:t=fill"
        gold_bar = f"drawbox=x=0:y=ih-14:w='iw*(t/{max(1.0, total_duration):.3f})':h=14:color=0xFFD700@0.95:t=fill"
        progress_filter = f"{dark_rail},{gold_bar}"

        # 1-Urinish: Progress-bar + ASS karaoke subtitrlar
        full_vf_with_sub = f"{progress_filter},ass={rel_ass}"
        cmd_with_subtitles = [
            "ffmpeg", "-nostdin", "-y",
            "-f", "concat", "-safe", "0",
            "-i", rel_concat,
            "-i", rel_audio,
            "-vf", full_vf_with_sub,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            rel_final
        ]

        try:
            res = subprocess.run(cmd_with_subtitles, cwd=str(BASE_DIR), capture_output=True, text=True, timeout=120)
            if res.returncode == 0 and os.path.exists(output_final_path) and os.path.getsize(output_final_path) > 1000:
                return output_final_path
            print(f"[VideoEngine Notice] ASS subtitr renderida xatolik: {res.stderr[:200]}")
        except Exception as e:
            print(f"[VideoEngine Notice] ASS render sinovi: {e}")

        # 2-Urinish (Zero-Defect Fallback): Faqat progress-bar bilan Full HD montaj
        cmd_fallback = [
            "ffmpeg", "-nostdin", "-y",
            "-f", "concat", "-safe", "0",
            "-i", rel_concat,
            "-i", rel_audio,
            "-vf", progress_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            rel_final
        ]
        subprocess.run(cmd_fallback, cwd=str(BASE_DIR), capture_output=True, check=True, timeout=120)
        return output_final_path
