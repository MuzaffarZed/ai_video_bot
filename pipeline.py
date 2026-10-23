"""
MuzaffarZed AI Video Bot - Yagona Boshqaruv Konveyeri (Pipeline 2.5)
Barcha bosqichlarni (Ssenariy, Ovoz, Tematik Kadrlar, Musiqa, Subtitr, Video) uyg'unlashtiradi.
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

from typing import Callable, Optional, Dict
from config import TEMP_DIR, OUTPUT_DIR, DEFAULT_VOICE, VOICES, DEFAULT_VOICE_MODE, VOICE_MODES
from script_generator import ScriptGenerator
from tts_engine import TTSEngine
from visual_engine import VisualEngine
from audio_mixer import AudioMixer
from subtitle_engine import SubtitleEngine
from video_engine import VideoEngine

class VideoPipeline:
    def __init__(self):
        self.script_gen = ScriptGenerator()
        self.visual_eng = VisualEngine()
        self.audio_mixer = AudioMixer()
        self.subtitle_eng = SubtitleEngine()
        self.video_eng = VideoEngine()

    async def create_video(
        self,
        topic: str,
        voice_key: str = DEFAULT_VOICE,
        voice_mode: str = DEFAULT_VOICE_MODE,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict:
        """
        To'liq professional siklda video tayyorlaydi (Studio 2.5).
        """
        task_id = f"job_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        total_steps = 5

        async def notify(step: int, msg: str):
            if progress_callback:
                try:
                    if asyncio.iscoroutinefunction(progress_callback):
                        await progress_callback(step, total_steps, msg)
                    else:
                        progress_callback(step, total_steps, msg)
                except Exception as e:
                    print(f"[Callback Error] {e}")

        # 1-Bosqich: Ssenariy
        await notify(1, "🧠 1/5: AI ssenariy va viral kadrlar tuzilmoqda...")
        lang = VOICES.get(voice_key, {}).get("lang", "uz")
        scenes = await asyncio.to_thread(self.script_gen.generate, topic, lang)

        # 2-Bosqich: Ovozlashtirish & Studiya DSP
        await notify(2, "🎙 2/5: Studiya DSP ovozi (EBU R128 + Warmth) yozilmoqda...")
        tts = TTSEngine(voice_key=voice_key, mode_key=voice_mode)
        processed_scenes = await tts.process_all_scenes(scenes, task_id=task_id)

        # 3-Bosqich: Mavzuga mos vizual kadrlar
        await notify(3, "🎨 3/5: Mavzuga mos 4K vertikal tasvirlar tanlanmoqda...")
        category = self.visual_eng.detect_category(topic)
        for sc in processed_scenes:
            img_path = str(TEMP_DIR / f"{task_id}_img_{sc['scene_num']}.jpg")
            prompt = sc.get("visual_prompt") or topic
            await asyncio.to_thread(self.visual_eng.get_scene_visual, prompt, img_path, None, sc["scene_num"])
            sc["image_path"] = img_path

        # 4-Bosqich: Mavzuga mos fon musiqasi & Sidechain Ducking & Subtitrlar
        await notify(4, "🎵 4/5: Fon musiqasi (Sidechain Ducking) va Karaoke tayyorlanmoqda...")
        voice_files = [sc["audio_path"] for sc in processed_scenes]
        master_audio = str(TEMP_DIR / f"{task_id}_master_audio.wav")
        music_genre = self.visual_eng.get_music_genre_for_category(category)
        await asyncio.to_thread(self.audio_mixer.mix, voice_files, master_audio, genre=music_genre)

        ass_path = str(TEMP_DIR / f"{task_id}_subtitles.ass")
        await asyncio.to_thread(self.subtitle_eng.generate_ass, processed_scenes, ass_path)

        # 5-Bosqich: Kliplarni render qilish va Final montaj
        await notify(5, "🎬 5/5: Dynamic Zoom & Pan va oltin progress-bar montaj qilinmoqda...")
        scene_clips = []
        for sc in processed_scenes:
            clip_path = str(TEMP_DIR / f"{task_id}_clip_{sc['scene_num']}.mp4")
            await asyncio.to_thread(
                self.video_eng.render_scene_clip,
                sc["image_path"],
                sc["duration"],
                clip_path,
                sc["scene_num"]
            )
            scene_clips.append(clip_path)

        total_duration = processed_scenes[-1]["end_time"] if processed_scenes else 0.0
        output_final = str(OUTPUT_DIR / f"{task_id}_final.mp4")
        await asyncio.to_thread(
            self.video_eng.assemble_final_video,
            scene_clips,
            master_audio,
            ass_path,
            output_final,
            total_duration
        )

        return {
            "status": "success",
            "video_path": output_final,
            "duration": total_duration,
            "scenes": processed_scenes,
            "task_id": task_id,
            "category": category,
            "music_genre": music_genre
        }

    @staticmethod
    def cleanup_task_files(task_id: str):
        """Vaqtincha render fayllarini diskdan tozalash."""
        try:
            for item in TEMP_DIR.glob(f"{task_id}_*"):
                try: item.unlink(missing_ok=True)
                except Exception: pass
        except Exception as e:
            print(f"[Cleanup Notice] {e}")
