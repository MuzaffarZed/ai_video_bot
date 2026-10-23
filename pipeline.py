"""
MuzaffarZed AI Video Bot - Yagona Boshqaruv Konveyeri (Pipeline)
Barcha bosqichlarni (Ssenariy, Ovoz, Kadrlar, Musiqa, Subtitr, Video) uyg'unlashtiradi.
Muallif: MuzaffarZed
"""
import os
import sys
import time
import uuid
import asyncio
from pathlib import Path

# Papka yo'lini sys.path ga kiritish
current_dir = str(Path(__file__).resolve().parent)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from typing import Callable, Optional, Dict
from config import TEMP_DIR, OUTPUT_DIR, DEFAULT_VOICE, VOICES
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
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict:
        """
        To'liq siklda video tayyorlaydi.
        progress_callback: f(step, total_steps, status_text)
        """
        task_id = f"job_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        total_steps = 5

        def update_progress(step: int, msg: str):
            if progress_callback:
                try:
                    if asyncio.iscoroutinefunction(progress_callback):
                        asyncio.create_task(progress_callback(step, total_steps, msg))
                    else:
                        progress_callback(step, total_steps, msg)
                except Exception as e:
                    print(f"[Callback Error] {e}")

        # 1-Bosqich: Ssenariy
        update_progress(1, "🧠 1/5: AI ssenariy va kadrlar taqsimoti tuzilmoqda...")
        lang = VOICES.get(voice_key, {}).get("lang", "uz")
        scenes = self.script_gen.generate(topic, lang=lang)

        # 2-Bosqich: Ovozlashtirish & Vaqtlar
        update_progress(2, "🎙 2/5: Tabiiy neyron ovozda nutq va vaqtlar hisoblanmoqda...")
        tts = TTSEngine(voice_key=voice_key)
        processed_scenes = await tts.process_all_scenes(scenes, task_id=task_id)

        # 3-Bosqich: Kadrlar Generatsiyasi
        update_progress(3, "🎨 3/5: Har bir kadr uchun yuqori aniqlikdagi AI tasvirlar chizilmoqda...")
        for sc in processed_scenes:
            img_path = str(TEMP_DIR / f"{task_id}_img_{sc['scene_num']}.jpg")
            prompt = sc.get("visual_prompt") or topic
            self.visual_eng.get_scene_visual(prompt, img_path)
            sc["image_path"] = img_path

        # 4-Bosqich: Musiqa & Audio Ducking & Subtitrlar
        update_progress(4, "🎵 4/5: Fon musiqasi (Audio Ducking) va Karaoke subtitrlar tayyorlanmoqda...")
        voice_files = [sc["audio_path"] for sc in processed_scenes]
        master_audio = str(TEMP_DIR / f"{task_id}_master_audio.wav")
        self.audio_mixer.mix(voice_files, master_audio)

        ass_path = str(TEMP_DIR / f"{task_id}_subtitles.ass")
        self.subtitle_eng.generate_ass(processed_scenes, ass_path)

        # 5-Bosqich: Kliplarni render qilish va Final montaj
        update_progress(5, "🎬 5/5: Subtitr va audio ulanib, Full HD video yig'ilmoqda...")
        scene_clips = []
        for sc in processed_scenes:
            clip_path = str(TEMP_DIR / f"{task_id}_clip_{sc['scene_num']}.mp4")
            self.video_eng.render_scene_clip(sc["image_path"], sc["duration"], clip_path)
            scene_clips.append(clip_path)

        output_final = str(OUTPUT_DIR / f"{task_id}_final.mp4")
        self.video_eng.assemble_final_video(
            scene_clips=scene_clips,
            master_audio_path=master_audio,
            ass_subtitle_path=ass_path,
            output_final_path=output_final
        )

        total_duration = processed_scenes[-1]["end_time"] if processed_scenes else 0.0

        return {
            "status": "success",
            "video_path": output_final,
            "duration": total_duration,
            "scenes": processed_scenes,
            "task_id": task_id
        }
