"""
MuzaffarZed AI Video Bot - Yagona Boshqaruv Konveyeri (Pipeline 6.0 Zenith)
Barcha bosqichlarni (Ssenariy, Ovoz, Kadrlar, Musiqa, Subtitr, Rang Filtri, SEO) uyg'unlashtiradi.
Muallif: MuzaffarZed
"""
import os
import sys
import time
import uuid
import random
import asyncio
import subprocess
from pathlib import Path

current_dir = str(Path(__file__).resolve().parent)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from typing import Callable, Optional, Dict, List
from config import (
    TEMP_DIR,
    OUTPUT_DIR,
    USER_UPLOADS_DIR,
    DEFAULT_VOICE,
    VOICES,
    DEFAULT_VOICE_MODE,
    AUDIO_EFFECTS,
    DEFAULT_AUDIO_EFFECT,
    DEFAULT_VIDEO_STYLE,
    DEFAULT_SUBTITLE_THEME,
    DEFAULT_SUBTITLE_SIZE,
    DEFAULT_MUSIC_GENRE,
    DEFAULT_DURATION,
    DEFAULT_FORMAT,
    DEFAULT_VISUAL_FILTER,
    DEFAULT_ART_STYLE,
    DEFAULT_CAMERA_MOTION,
    FORMATS
)
from script_generator import ScriptGenerator
from tts_engine import TTSEngine
from visual_engine import VisualEngine
from audio_mixer import AudioMixer
from subtitle_engine import SubtitleEngine
from video_engine import VideoEngine

class VideoPipeline:
    def __init__(self):
        self.script_gen = ScriptGenerator()
        self.audio_mixer = AudioMixer()
        self.subtitle_eng = SubtitleEngine()
        self.video_eng = VideoEngine()
        self.visual_eng = VisualEngine()

    async def create_video(
        self,
        topic: str,
        voice_key: str = DEFAULT_VOICE,
        voice_mode: str = DEFAULT_VOICE_MODE,
        effect_key: str = DEFAULT_AUDIO_EFFECT,
        style_key: str = DEFAULT_VIDEO_STYLE,
        theme_key: str = DEFAULT_SUBTITLE_THEME,
        music_key: str = DEFAULT_MUSIC_GENRE,
        duration_key: str = DEFAULT_DURATION,
        format_key: str = DEFAULT_FORMAT,
        filter_key: str = DEFAULT_VISUAL_FILTER,
        motion_key: str = DEFAULT_CAMERA_MOTION,
        size_key: str = DEFAULT_SUBTITLE_SIZE,
        art_style: str = DEFAULT_ART_STYLE,
        bgm_volume: float = 0.15,
        custom_scenes: Optional[List[Dict]] = None,
        custom_image_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict:
        """
        To'liq professional siklda video, MP3 va SEO paketini tayyorlaydi (Zenith 16.0).
        """
        task_id = f"job_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        total_steps = 5

        visual_eng = VisualEngine(format_key=format_key)

        async def notify(step: int, msg: str):
            if progress_callback:
                try:
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(step, total_steps, msg)
                    else:
                        progress_callback(step, total_steps, msg)
                except Exception as e:
                    print(f"[Callback Error] {e}")

        # 1-Bosqich: Ssenariy va SEO paket
        await notify(1, "🧠 1/5: AI ssenariy va viral kadrlar tuzilmoqda...")
        lang = VOICES.get(voice_key, {}).get("lang", "uz")
        if custom_scenes:
            scenes = custom_scenes
        else:
            scenes = await asyncio.to_thread(self.script_gen.generate, topic, lang, style_key, duration_key, voice_mode)
        seo_data = await asyncio.to_thread(self.script_gen.generate_viral_seo_package, topic, lang, scenes)

        # 2-Bosqich: Ovozlashtirish & Studiya DSP
        await notify(2, "🎙 2/5: Studiya DSP ovozi (EBU R128 + Warmth) yozilmoqda...")
        tts = TTSEngine(voice_key=voice_key, mode_key=voice_mode, effect_key=effect_key)
        processed_scenes = await tts.process_all_scenes(scenes, task_id=task_id)

        # 3-Bosqich: 8K AI tasvirlar (Pollinations AI + 4K Unsplash)
        await notify(3, "🎨 3/5: Real-Time AI kadrlar chizilmoqda va vinyetka berilmoqda...")
        category = visual_eng.detect_category(topic)

        async def fetch_scene_visual(sc):
            img_path = str(TEMP_DIR / f"{task_id}_img_{sc['scene_num']}.jpg")
            if custom_image_path and os.path.exists(custom_image_path) and sc["scene_num"] == 1:
                await asyncio.to_thread(visual_eng.process_custom_user_image, custom_image_path, img_path)
            else:
                prompt = sc.get("visual_prompt") or topic
                await asyncio.to_thread(visual_eng.get_scene_visual, prompt, img_path, None, sc["scene_num"], art_style)
            sc["image_path"] = img_path

        await asyncio.gather(*[fetch_scene_visual(sc) for sc in processed_scenes])

        # 4-Bosqich: Musiqa, Ducking, Subtitr & Podkast MP3
        await notify(4, "🎵 4/5: Fon musiqasi (Sidechain Ducking) va Karaoke tayyorlanmoqda...")
        voice_files = [sc["audio_path"] for sc in processed_scenes]
        master_audio = str(TEMP_DIR / f"{task_id}_master_audio.wav")
        clean_voice_wav = str(TEMP_DIR / f"{task_id}_vocals.wav")

        final_music_genre = music_key
        if final_music_genre == "auto" or not final_music_genre:
            final_music_genre = visual_eng.get_music_genre_for_category(category)

        transition_points = [sc["end_time"] for sc in processed_scenes[:-1]] if len(processed_scenes) > 1 else []
        await asyncio.to_thread(
            self.audio_mixer.mix,
            voice_files,
            master_audio,
            genre=final_music_genre,
            transition_points=transition_points,
            bgm_volume=bgm_volume,
            output_vocals_path=clean_voice_wav
        )

        # Alohida MP3 podkast
        output_mp3 = str(OUTPUT_DIR / f"{task_id}_podcast.mp3")
        await asyncio.to_thread(self.audio_mixer.export_mp3_podcast, master_audio, output_mp3)

        # Alohida toza nutq (Vocals only) eksporti
        clean_voice_mp3 = str(OUTPUT_DIR / f"{task_id}_vocals.mp3")
        if os.path.exists(clean_voice_wav):
            try:
                await asyncio.to_thread(self.audio_mixer.export_mp3_podcast, clean_voice_wav, clean_voice_mp3)
            except Exception as v_err:
                print(f"[Vocals Export Notice] {v_err}")
                clean_voice_mp3 = None
        else:
            clean_voice_mp3 = None

        ass_path = str(TEMP_DIR / f"{task_id}_subtitles.ass")
        await asyncio.to_thread(
            self.subtitle_eng.generate_ass,
            processed_scenes,
            ass_path,
            theme_key=theme_key,
            format_key=format_key,
            size_key=size_key,
            topic_badge=topic
        )

        # Alohida SRT subtitr fayli eksporti
        srt_path = str(OUTPUT_DIR / f"{task_id}_subtitles.srt")
        await asyncio.to_thread(self.subtitle_eng.generate_srt, processed_scenes, srt_path)

        # Video uchun maxsus muqova (thumbnail) va Full HD poster kartochkasi
        thumb_path = str(TEMP_DIR / f"{task_id}_thumb.jpg")
        poster_path = str(OUTPUT_DIR / f"{task_id}_poster.jpg")
        if processed_scenes:
            first_img = processed_scenes[0]["image_path"]
            await asyncio.to_thread(visual_eng.generate_thumbnail_card, first_img, topic, thumb_path)
            await asyncio.to_thread(visual_eng.generate_cover_poster, first_img, topic, poster_path)

        # 5-Bosqich: Kinematografik LUT render va Final montaj
        await notify(5, "🎬 5/5: Kinematografik rang grading va montaj yakunlanmoqda...")

        async def render_single_clip(sc):
            clip_path = str(TEMP_DIR / f"{task_id}_clip_{sc['scene_num']}.mp4")
            await asyncio.to_thread(
                self.video_eng.render_scene_clip,
                sc["image_path"],
                sc["duration"],
                clip_path,
                sc["scene_num"],
                format_key,
                filter_key,
                motion_key
            )
            return clip_path

        scene_clips = await asyncio.gather(*[render_single_clip(sc) for sc in processed_scenes])

        total_duration = processed_scenes[-1]["end_time"] if processed_scenes else 0.0
        output_final = str(OUTPUT_DIR / f"{task_id}_final.mp4")
        await asyncio.to_thread(
            self.video_eng.assemble_final_video,
            scene_clips,
            master_audio,
            ass_path,
            output_final,
            total_duration,
            theme_key=theme_key,
            format_key=format_key
        )

        full_script_text = "\n\n".join([f"Kadr {s['scene_num']}: {s['text']}" for s in processed_scenes])

        return {
            "status": "success",
            "video_path": output_final,
            "mp3_path": output_mp3,
            "vocals_path": clean_voice_mp3 if clean_voice_mp3 and os.path.exists(clean_voice_mp3) else None,
            "srt_path": srt_path,
            "thumb_path": thumb_path if os.path.exists(thumb_path) else None,
            "poster_path": poster_path if os.path.exists(poster_path) else None,
            "script_text": full_script_text,
            "seo_package": seo_data,
            "duration": total_duration,
            "scenes": processed_scenes,
            "task_id": task_id,
            "category": category,
            "music_genre": final_music_genre,
            "format_key": format_key,
            "filter_key": filter_key,
            "motion_key": motion_key,
            "master_audio_path": master_audio
        }

    @staticmethod
    def can_fast_reformat(scenes: List[Dict], master_audio_path: str) -> bool:
        if not scenes or not master_audio_path or not os.path.exists(master_audio_path):
            return False
        for sc in scenes:
            img = sc.get("image_path")
            if not img or not os.path.exists(img):
                return False
        return True

    async def fast_reformat_video(
        self,
        task_id: str,
        scenes: List[Dict],
        master_audio_path: str,
        new_format_key: str,
        theme_key: str = DEFAULT_SUBTITLE_THEME,
        filter_key: str = DEFAULT_VISUAL_FILTER,
        motion_key: str = DEFAULT_CAMERA_MOTION,
        size_key: str = DEFAULT_SUBTITLE_SIZE,
        topic: str = "Video"
    ) -> Dict:
        """
        Mavjud ovoz va suratlarni qayta yuklamasdan 3 soniyada yangi formatga (16:9 yoki 9:16) o'giradi.
        """
        clean_fmt = new_format_key.replace(":", "_")
        reformat_task_id = f"{task_id}_{clean_fmt}"
        visual_eng = VisualEngine(format_key=new_format_key)

        ass_path = str(TEMP_DIR / f"{reformat_task_id}_subtitles.ass")
        await asyncio.to_thread(
            self.subtitle_eng.generate_ass,
            scenes,
            ass_path,
            theme_key=theme_key,
            format_key=new_format_key,
            size_key=size_key,
            topic_badge=topic
        )

        poster_path = str(OUTPUT_DIR / f"{reformat_task_id}_poster.jpg")
        if scenes:
            await asyncio.to_thread(visual_eng.generate_cover_poster, scenes[0]["image_path"], topic, poster_path)

        async def render_single_clip(sc):
            clip_path = str(TEMP_DIR / f"{reformat_task_id}_clip_{sc['scene_num']}.mp4")
            await asyncio.to_thread(
                self.video_eng.render_scene_clip,
                sc["image_path"],
                sc["duration"],
                clip_path,
                sc["scene_num"],
                new_format_key,
                filter_key,
                motion_key
            )
            return clip_path

        scene_clips = await asyncio.gather(*[render_single_clip(sc) for sc in scenes])

        total_duration = scenes[-1]["end_time"] if scenes else 0.0
        output_final = str(OUTPUT_DIR / f"{reformat_task_id}_final.mp4")
        await asyncio.to_thread(
            self.video_eng.assemble_final_video,
            scene_clips,
            master_audio_path,
            ass_path,
            output_final,
            total_duration,
            theme_key=theme_key,
            format_key=new_format_key
        )

        return {
            "status": "success",
            "video_path": output_final,
            "poster_path": poster_path if os.path.exists(poster_path) else None,
            "format_key": new_format_key,
            "duration": total_duration,
            "task_id": reformat_task_id
        }

    async def reroll_visuals_for_video(
        self,
        task_id: str,
        scenes: List[Dict],
        master_audio_path: str,
        format_key: str = DEFAULT_FORMAT,
        theme_key: str = DEFAULT_SUBTITLE_THEME,
        filter_key: str = DEFAULT_VISUAL_FILTER,
        motion_key: str = DEFAULT_CAMERA_MOTION,
        size_key: str = DEFAULT_SUBTITLE_SIZE,
        art_style: str = DEFAULT_ART_STYLE,
        topic: str = "Video"
    ) -> Dict:
        """
        Mavjud ssenariy va ovozni saqlab qolgan holda butunlay yangi AI kadrlarni chizadi va 4 soniyada montaj qiladi.
        """
        clean_task_id = f"{task_id}_reroll_{int(time.time())}"
        visual_eng = VisualEngine(format_key=format_key)

        async def fetch_fresh_visual(sc):
            img_path = str(TEMP_DIR / f"{clean_task_id}_img_{sc['scene_num']}.jpg")
            prompt = f"{sc.get('visual_prompt', topic)}, variation {random.randint(100, 9999)}"
            await asyncio.to_thread(visual_eng.get_scene_visual, prompt, img_path, None, sc["scene_num"], art_style)
            new_sc = dict(sc)
            new_sc["image_path"] = img_path
            return new_sc

        updated_scenes = await asyncio.gather(*[fetch_fresh_visual(sc) for sc in scenes])

        poster_path = str(OUTPUT_DIR / f"{clean_task_id}_poster.jpg")
        if updated_scenes:
            await asyncio.to_thread(visual_eng.generate_cover_poster, updated_scenes[0]["image_path"], topic, poster_path)

        ass_path = str(TEMP_DIR / f"{clean_task_id}_subtitles.ass")
        await asyncio.to_thread(
            self.subtitle_eng.generate_ass,
            updated_scenes,
            ass_path,
            theme_key=theme_key,
            format_key=format_key,
            size_key=size_key,
            topic_badge=topic
        )

        async def render_single_clip(sc):
            clip_path = str(TEMP_DIR / f"{clean_task_id}_clip_{sc['scene_num']}.mp4")
            await asyncio.to_thread(
                self.video_eng.render_scene_clip,
                sc["image_path"],
                sc["duration"],
                clip_path,
                sc["scene_num"],
                format_key,
                filter_key,
                motion_key
            )
            return clip_path

        scene_clips = await asyncio.gather(*[render_single_clip(sc) for sc in updated_scenes])

        total_duration = updated_scenes[-1]["end_time"] if updated_scenes else 0.0
        output_final = str(OUTPUT_DIR / f"{clean_task_id}_final.mp4")
        await asyncio.to_thread(
            self.video_eng.assemble_final_video,
            scene_clips,
            master_audio_path,
            ass_path,
            output_final,
            total_duration,
            theme_key=theme_key,
            format_key=format_key
        )

        return {
            "status": "success",
            "video_path": output_final,
            "poster_path": poster_path if os.path.exists(poster_path) else None,
            "scenes": updated_scenes,
            "format_key": format_key,
            "duration": total_duration,
            "task_id": clean_task_id
        }

    @staticmethod
    def cleanup_old_temp_files(max_age_hours: float = 1.0):
        """1 soatdan eski vaqtinchalik va 24 soatdan eski foydalanuvchi yuklamalarini xavfsiz tozalash."""
        now = time.time()
        cutoff_temp = now - (max_age_hours * 3600)
        cutoff_uploads = now - (24.0 * 3600)
        try:
            for item in TEMP_DIR.iterdir():
                if item.is_file() and item.stat().st_mtime < cutoff_temp:
                    try: item.unlink(missing_ok=True)
                    except Exception: pass
        except Exception as e:
            print(f"[Garbage Collection Temp Notice] {e}")

        try:
            for item in USER_UPLOADS_DIR.iterdir():
                if item.is_file() and item.stat().st_mtime < cutoff_uploads:
                    try: item.unlink(missing_ok=True)
                    except Exception: pass
        except Exception as e:
            print(f"[Garbage Collection Uploads Notice] {e}")

    @staticmethod
    def cleanup_task_files(task_id: str):
        try:
            for item in TEMP_DIR.glob(f"{task_id}_*"):
                try: item.unlink(missing_ok=True)
                except Exception: pass
        except Exception as e:
            print(f"[Cleanup Notice] {e}")

    @staticmethod
    async def extract_story_snippet(video_path: str, output_path: str, duration: float = 15.0) -> str:
        """
        Telegram va WhatsApp Stories uchun videoning birinchi 15 soniyasini
        o'ta tezkor (fast re-encode) tarzda qirqib beradi.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video fayli topilmadi: {video_path}")

        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-ss", "00:00:00",
            "-i", video_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path
        ]

        def run_ffmpeg():
            subprocess.run(cmd, capture_output=True, check=True, timeout=45)

        await asyncio.to_thread(run_ffmpeg)
        return output_path

    @staticmethod
    async def change_video_speed(video_path: str, output_path: str, speed: float = 1.25) -> str:
        """
        Videoni tezlashtirish (masalan 1.25x) yoki sekinlashtirish (0.85x) —
        ovoz toni buzilmasdan (pitch-preserving atempo) va o'ta tezkor (ultrafast) render.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video fayli topilmadi: {video_path}")

        filter_str = f"[0:v]setpts=PTS/{speed}[v];[0:a]atempo={speed}[a]"
        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-i", video_path,
            "-filter_complex", filter_str,
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path
        ]

        def run_ffmpeg():
            subprocess.run(cmd, capture_output=True, check=True, timeout=60)

        await asyncio.to_thread(run_ffmpeg)
        return output_path
