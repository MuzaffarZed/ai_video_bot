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
    CAMERA_MOTIONS,
    DEFAULT_CAMERA_MOTION,
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
        filter_key: str = DEFAULT_VISUAL_FILTER,
        motion_key: str = DEFAULT_CAMERA_MOTION
    ) -> str:
        """
        Bitta rasmdan kinematografik suzuvchi kamera harakati (Dynamic Drift, Shok Punch, Static)
        va tanlangan rang filtri (LUT) bilan Full HD klip hosil qiladi.
        """
        fmt = FORMATS.get(format_key, FORMATS[DEFAULT_FORMAT])
        target_w = fmt["width"]
        target_h = fmt["height"]

        clean_img = os.path.relpath(image_path, BASE_DIR).replace("\\", "/")
        clean_out = os.path.relpath(output_clip_path, BASE_DIR).replace("\\", "/")

        motion_data = CAMERA_MOTIONS.get(motion_key, CAMERA_MOTIONS.get(DEFAULT_CAMERA_MOTION, {"zoom": 1.15, "speed": 1.0, "mode": "drift"}))
        zoom_val = motion_data.get("zoom", 1.15)
        speed_factor = motion_data.get("speed", 1.0)
        mode = motion_data.get("mode", "drift")

        scaled_w = int(target_w * zoom_val)
        scaled_h = int(target_h * zoom_val)

        filter_data = VISUAL_FILTERS.get(filter_key, VISUAL_FILTERS[DEFAULT_VISUAL_FILTER])
        color_filter = filter_data.get("filter", "eq=contrast=1.06:saturation=1.14")

        fade_d = min(0.20, duration * 0.1)
        fade_out_st = max(0.0, duration - fade_d)
        fades = f"fade=t=in:st=0:d={fade_d:.3f},fade=t=out:st={fade_out_st:.3f}:d={fade_d:.3f}"

        if mode == "zoom_in":
            vf_filter = (
                f"zoompan=z='min(zoom+0.0016,1.22)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={target_w}x{target_h}:fps={self.fps},"
                f"{color_filter},"
                f"{fades},"
                f"setsar=1"
            )
        elif mode == "pan_horiz":
            if scene_idx % 2 == 1:
                pan_x = f"(in_w-out_w)*(t/{max(0.1, duration):.3f})"
            else:
                pan_x = f"(in_w-out_w)*(1 - t/{max(0.1, duration):.3f})"
            pan_y = "(in_h-out_h)/2"
            vf_filter = (
                f"scale={scaled_w}:{scaled_h}:force_original_aspect_ratio=increase,crop={scaled_w}:{scaled_h},"
                f"crop={target_w}:{target_h}:x='{pan_x}':y='{pan_y}',"
                f"{color_filter},"
                f"{fades},"
                f"setsar=1"
            )
        else:
            if speed_factor <= 0.001:
                drift_x = "(in_w-out_w)/2"
                drift_y = "(in_h-out_h)/2"
            elif scene_idx % 2 == 1:
                drift_x = f"(in_w-out_w)/2 + sin(t*{1.1 * speed_factor:.2f})*{int(target_w * 0.035 * speed_factor)}"
                drift_y = f"(in_h-out_h)/2 + (t/10)*{int(target_h * 0.015 * speed_factor)}"
            else:
                drift_x = f"(in_w-out_w)/2 - sin(t*{1.1 * speed_factor:.2f})*{int(target_w * 0.035 * speed_factor)}"
                drift_y = f"(in_h-out_h)/2 - (t/10)*{int(target_h * 0.012 * speed_factor)}"

            vf_filter = (
                f"scale={scaled_w}:{scaled_h}:force_original_aspect_ratio=increase,crop={scaled_w}:{scaled_h},"
                f"crop={target_w}:{target_h}:x='{drift_x}':y='{drift_y}',"
                f"{color_filter},"
                f"{fades},"
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
        task_tag = os.path.splitext(os.path.basename(output_final_path))[0]
        concat_txt = TEMP_DIR / f"clips_concat_{task_tag}.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for clip in scene_clips:
                clean_path = os.path.abspath(clip).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        rel_concat = os.path.abspath(str(concat_txt)).replace("\\", "/")
        rel_audio = os.path.abspath(master_audio_path).replace("\\", "/")
        rel_ass = os.path.relpath(ass_subtitle_path, BASE_DIR).replace("\\", "/") if ass_subtitle_path else ""
        escaped_ass = rel_ass.replace(":", "\\\\:")
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
            full_vf = f"{progress_filter},ass='{escaped_ass}'"
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
        finally:
            if os.path.exists(concat_txt):
                try: os.remove(concat_txt)
                except Exception: pass

    def render_voice_waveform_video(
        self,
        image_path: str,
        audio_path: str,
        output_video_path: str,
        format_key: str = DEFAULT_FORMAT
    ) -> str:
        """
        Ovozli xabar yoki podkast uchun jonli animatsiyali neon to'lqin (Audiogram waveform)
        va kinematografik fon bilan yuqori sifatli video yaratadi.
        """
        fmt = FORMATS.get(format_key, FORMATS[DEFAULT_FORMAT])
        target_w = fmt["width"]
        target_h = fmt["height"]

        wave_w = int(target_w * 0.82)
        wave_h = int(target_h * 0.15)
        wave_y = int(target_h * 0.68)

        clean_img = os.path.relpath(image_path, BASE_DIR).replace("\\", "/")
        clean_aud = os.path.relpath(audio_path, BASE_DIR).replace("\\", "/")
        clean_out = os.path.relpath(output_video_path, BASE_DIR).replace("\\", "/")

        wave_filter = (
            f"[1:a]showwaves=s={wave_w}x{wave_h}:mode=line:colors=0x00FFFF@0.85|0x00FF7F@0.85[wave];"
            f"[0:v]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},"
            f"boxblur=luma_radius=10:luma_power=2,eq=contrast=1.08:brightness=-0.04[bg];"
            f"[bg][wave]overlay=(W-w)/2:{wave_y}[v1];"
            f"[v1]drawbox=x=0:y=ih-12:w=iw:h=12:color=0x00FFFF@0.8:t=fill,"
            f"drawtext=text='{BRAND_NAME}':x=(w-text_w)/2:y={int(target_h*0.14)}:fontsize={int(target_w*0.045)}:fontcolor=white:shadowcolor=black@0.7:shadowx=2:shadowy=2,"
            f"drawtext=text='{WATERMARK_TEXT}':x=(w-text_w)/2:y=h-{int(target_h*0.06)}:fontsize={int(target_w*0.032)}:fontcolor=white@0.7[vout]"
        )

        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-loop", "1", "-i", clean_img,
            "-i", clean_aud,
            "-filter_complex", wave_filter,
            "-map", "[vout]", "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-threads", "2",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-movflags", "+faststart",
            clean_out
        ]
        subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, check=True, timeout=120)
        return output_video_path
