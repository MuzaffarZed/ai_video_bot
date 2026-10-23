"""
MuzaffarZed AI Video Bot - Ovozlashtirish va Vaqt O'lchash Dvigateli
Edge-TTS yordamida studiya darajasidagi ovoz va aniq so'zma-so'z vaqtlar.
Muallif: MuzaffarZed
"""
import os
import asyncio
import subprocess
import json
from typing import List, Dict
import edge_tts
from config import TEMP_DIR, VOICES, DEFAULT_VOICE

class TTSEngine:
    def __init__(self, voice_key: str = DEFAULT_VOICE):
        if voice_key not in VOICES:
            voice_key = DEFAULT_VOICE
        self.voice_info = VOICES[voice_key]
        self.voice_id = self.voice_info["id"]

    async def generate_scene_audio(self, text: str, output_path: str) -> float:
        """
        Bitta kadr matnini ovozlashtiradi va faylga saqlaydi.
        Qaytaradi: audio davomiyligi (soniyalarda).
        """
        comm = edge_tts.Communicate(text, self.voice_id)
        await comm.save(output_path)
        return self.get_audio_duration(output_path)

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """
        ffprobe yordamida audioning aniq davomiyligini oladi.
        """
        try:
            cmd = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(res.stdout.strip())
        except Exception as e:
            print(f"[Error ffprobe] {e}")
            return 3.5

    def build_word_timings(self, text: str, start_offset: float, total_duration: float) -> List[Dict]:
        """
        Berilgan matn so'zlarining boshlanish va tugash vaqtlarini
        harflar va bo'g'inlar og'irligi bo'yicha millisekundgacha hisoblaydi.
        """
        words = text.strip().split()
        if not words:
            return []

        # Har bir so'zning harf og'irligi (tinish belgilarini hisobga olgan holda)
        weights = [max(1, len(w)) for w in words]
        total_weight = sum(weights)

        # Gap boshidagi va oxiridagi kichik pauza (0.15s)
        pad = min(0.15, total_duration * 0.05)
        active_duration = max(0.5, total_duration - (2 * pad))

        word_timings = []
        current_time = start_offset + pad

        for i, word in enumerate(words):
            fraction = weights[i] / total_weight
            duration = active_duration * fraction
            w_start = round(current_time, 3)
            w_end = round(current_time + duration, 3)
            word_timings.append({
                "word": word,
                "start": w_start,
                "end": w_end
            })
            current_time += duration

        return word_timings

    async def process_all_scenes(self, scenes: List[Dict], task_id: str = "job") -> List[Dict]:
        """
        Barcha kadrlarni ovozlashtiradi va umumiy vaqt chizig'ini tuzadi.
        """
        processed_scenes = []
        global_timeline_offset = 0.0

        for i, sc in enumerate(scenes):
            scene_idx = i + 1
            audio_path = str(TEMP_DIR / f"{task_id}_audio_{scene_idx}.mp3")
            
            # Ovoz hosil qilish
            dur = await self.generate_scene_audio(sc["text"], audio_path)
            
            # So'zlar vaqti
            timed_words = self.build_word_timings(sc["text"], global_timeline_offset, dur)

            scene_record = {
                "scene_num": scene_idx,
                "text": sc["text"],
                "visual_prompt": sc.get("visual_prompt", ""),
                "audio_path": audio_path,
                "duration": dur,
                "start_time": global_timeline_offset,
                "end_time": global_timeline_offset + dur,
                "words": timed_words
            }
            processed_scenes.append(scene_record)
            global_timeline_offset += dur

        return processed_scenes
