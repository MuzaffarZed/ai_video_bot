"""
MuzaffarZed AI Video Bot - Ovozlashtirish va Studiya DSP Dvigateli (Audio 2.0)
Edge-TTS + Studio Broadcast DSP (Ekvalayzer, Kompressiya, Warmth, Rezonans)
Muallif: MuzaffarZed
"""
import os
import asyncio
import subprocess
import json
from typing import List, Dict
import edge_tts
from config import TEMP_DIR, VOICES, DEFAULT_VOICE, VOICE_MODES, DEFAULT_VOICE_MODE

class TTSEngine:
    def __init__(self, voice_key: str = DEFAULT_VOICE, mode_key: str = DEFAULT_VOICE_MODE):
        if voice_key not in VOICES:
            voice_key = DEFAULT_VOICE
        self.voice_info = VOICES[voice_key]
        self.voice_id = self.voice_info["id"]

        mode_data = VOICE_MODES.get(mode_key, VOICE_MODES[DEFAULT_VOICE_MODE])
        self.rate = mode_data.get("rate", "+12%")
        self.pitch = mode_data.get("pitch", "-1Hz")

    async def generate_scene_audio(self, text: str, output_path: str) -> float:
        """
        Bitta kadr matnini ovozlashtiradi, Studiya DSP filtri bilan boyitadi va saqlaydi.
        """
        temp_raw = output_path + ".raw.mp3"
        comm = edge_tts.Communicate(text, self.voice_id, rate=self.rate, pitch=self.pitch)
        await comm.save(temp_raw)

        # Studiya Broadcast DSP zanjiri:
        # 1. 80Hz pastki shovqinlarni kesish
        # 2. 220Hz ko'krak rezonansi (iliq bas)
        # 3. 3600Hz nutq ravshanligi va konsonantlar tiniqligi
        # 4. Compand dinamik kompressor (bir xil qalin va barqaror studiya ovozi)
        dsp_filter = (
            "highpass=f=80,"
            "equalizer=f=220:t=q:w=1.2:g=2.8,"
            "equalizer=f=3600:t=q:w=1.0:g=3.2,"
            "compand=attacks=0.02:decays=0.1:points=-80/-80|-25/-15|-10/-5|0/0:soft-knee=6,"
            "volume=1.25"
        )

        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-i", temp_raw,
            "-af", dsp_filter,
            "-c:a", "pcm_s16le",
            output_path
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
        except Exception as e:
            # Fallback
            cmd_fb = ["ffmpeg", "-nostdin", "-y", "-i", temp_raw, "-c:a", "pcm_s16le", output_path]
            subprocess.run(cmd_fb, capture_output=True, check=True, timeout=30)
        finally:
            if os.path.exists(temp_raw):
                try: os.remove(temp_raw)
                except Exception: pass

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
            res = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=20)
            return float(res.stdout.strip())
        except Exception as e:
            print(f"[Error ffprobe] {e}")
            return 3.5

    def build_word_timings(self, text: str, start_offset: float, total_duration: float) -> List[Dict]:
        """
        Bo'g'inlar va tinish belgilari akustikasiga asoslangan millisekundlik vaqt hisoblagich.
        """
        words = text.strip().split()
        if not words:
            return []

        vowels = set("aeiouyаеёиоуыэюя")
        
        # Har bir so'zning bo'g'in og'irligi (unli harflar + harf uzunligi)
        word_weights = []
        for w in words:
            w_clean = w.lower()
            syllables = sum(1 for c in w_clean if c in vowels)
            weight = max(1.0, syllables * 1.5 + len(w_clean) * 0.4)
            word_weights.append(weight)

        total_weight = sum(word_weights)

        # Gap boshidagi va oxiridagi mayin nafas pauzasi
        lead_pad = min(0.10, total_duration * 0.03)
        tail_pad = min(0.12, total_duration * 0.04)
        active_duration = max(0.4, total_duration - lead_pad - tail_pad)

        word_timings = []
        current_time = start_offset + lead_pad

        for i, word in enumerate(words):
            fraction = word_weights[i] / total_weight
            base_dur = active_duration * fraction

            # Tinish belgilariga qarab mayin pauza qo'shish
            extra_pause = 0.0
            if word.endswith((",", ";", "-")):
                extra_pause = min(0.14, base_dur * 0.25)
            elif word.endswith((".", "!", "?", ":")):
                extra_pause = min(0.24, base_dur * 0.35)

            actual_word_dur = max(0.15, base_dur - extra_pause)
            w_start = round(current_time, 3)
            w_end = round(current_time + actual_word_dur, 3)

            word_timings.append({
                "word": word,
                "start": w_start,
                "end": w_end
            })
            current_time += base_dur

        return word_timings

    async def process_all_scenes(self, scenes: List[Dict], task_id: str = "job") -> List[Dict]:
        processed_scenes = []
        global_timeline_offset = 0.0

        for i, sc in enumerate(scenes):
            scene_idx = i + 1
            audio_path = str(TEMP_DIR / f"{task_id}_audio_{scene_idx}.wav")

            dur = await self.generate_scene_audio(sc["text"], audio_path)
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
