"""
MuzaffarZed AI Video Bot - Video Montaj va Rendiring Dvigateli
FFmpeg orqali kadrlarni tezkor birlashtirish, karaoke subtitr va audio ulanishi.
Muallif: MuzaffarZed
"""
import os
import subprocess
from typing import List, Dict
from config import BASE_DIR, TEMP_DIR, OUTPUT_DIR, FPS

class VideoEngine:
    def __init__(self, fps: int = FPS):
        self.fps = fps

    def render_scene_clip(self, image_path: str, duration: float, output_clip_path: str) -> str:
        """
        Bitta rasmdan berilgan soniyalik Full HD (1080x1920) video klip hosil qiladi.
        """
        clean_img = os.path.relpath(image_path, BASE_DIR).replace("\\", "/")
        clean_out = os.path.relpath(output_clip_path, BASE_DIR).replace("\\", "/")

        vf_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"

        cmd = [
            "ffmpeg", "-y",
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

        subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, check=True)
        return output_clip_path

    def assemble_final_video(
        self,
        scene_clips: List[str],
        master_audio_path: str,
        ass_subtitle_path: str,
        output_final_path: str
    ) -> str:
        """
        Barcha kadr kliplarini birlashtiradi, ovozni ulaydi va karaoke subtitrni yondiradi.
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

        cmd_final = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", rel_concat,
            "-i", rel_audio,
            "-vf", f"ass={rel_ass}",
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

        subprocess.run(cmd_final, cwd=str(BASE_DIR), capture_output=True, check=True)
        return output_final_path
