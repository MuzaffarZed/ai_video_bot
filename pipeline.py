"""
MuzaffarZed AI Video Bot - Yagona Boshqaruv Konveyeri (Pipeline 6.0 Zenith)
Barcha bosqichlarni (Ssenariy, Ovoz, Kadrlar, Musiqa, Subtitr, Rang Filtri, SEO) uyg'unlashtiradi.
Muallif: MuzaffarZed
"""
import os
import sys
import time
import uuid
import asyncio
from pathlib import Path

current_dir = str(Path(__file__).resolve().parent)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from typing import Callable, Optional, Dict, List
from config import (
    TEMP_DIR,
    OUTPUT_DIR,
    DEFAULT_VOICE,
    VOICES,
    DEFAULT_VOICE_MODE,
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
        To'liq professional siklda video, MP3 va SEO paketini tayyorlaydi (Zenith 6.0).
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
            scenes = await asyncio.to_thread(self.script_gen.generate, topic, lang, style_key, duration_key)
        seo_data = await asyncio.to_thread(self.script_gen.generate_viral_seo_package, topic, lang)

        # 2-Bosqich: Ovozlashtirish & Studiya DSP
        await notify(2, "🎙 2/5: Studiya DSP ovozi (EBU R128 + Warmth) yozilmoqda...")
        tts = TTSEngine(voice_key=voice_key, mode_key=voice_mode)
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
            bgm_volume=bgm_volume
        )

        # Alohida MP3 podkast
        output_mp3 = str(OUTPUT_DIR / f"{task_id}_podcast.mp3")
        await asyncio.to_thread(self.audio_mixer.export_mp3_podcast, master_audio, output_mp3)

        ass_path = str(TEMP_DIR / f"{task_id}_subtitles.ass")
        await asyncio.to_thread(
            self.subtitle_eng.generate_ass,
            processed_scenes,
            ass_path,
            theme_key=theme_key,
            format_key=format_key,
            size_key=size_key
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
            "motion_key": motion_key
        }

    @staticmethod
    def cleanup_task_files(task_id: str):
        try:
            for item in TEMP_DIR.glob(f"{task_id}_*"):
                try: item.unlink(missing_ok=True)
                except Exception: pass
        except Exception as e:
            print(f"[Cleanup Notice] {e}")
