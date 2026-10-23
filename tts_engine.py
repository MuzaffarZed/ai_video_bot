"""
MuzaffarZed AI Video Bot - Ovozlashtirish va Studiya DSP Dvigateli (Audio 9.0 Quantum Multi-Speaker)
Edge-TTS + Studio Broadcast DSP (Ekvalayzer, Kompressiya, EBU R128) va Ikki kishilik Podkast Ovoz Almashish.
Muallif: MuzaffarZed
"""
import os
import asyncio
import subprocess
import json
from typing import List, Dict
import edge_tts
from config import TEMP_DIR, VOICES, DEFAULT_VOICE, VOICE_MODES, DEFAULT_VOICE_MODE, AUDIO_EFFECTS, DEFAULT_AUDIO_EFFECT
from script_generator import transliterate_uzbek

VOICE_DEMO_TEXTS = {
    "uz_sardor": "Assalomu alaykum! Men Sardor — sizning videolaringiz uchun rasmiy va salobatli ovozman.",
    "uz_madina": "Assalomu alaykum! Men Madina — ilhomlantiruvchi, mayin va jozibador ovozman.",
    "ru_dmitry": "Здравствуйте! Я Дмитрий — ваш уверенный и профессиональный дикторский голос.",
    "ru_svetlana": "Привет! Я Светлана — вдохновляющий и выразительный женский голос.",
    "en_christopher": "Hello! I am Christopher — your dynamic and cinematic English narrator.",
    "en_aria": "Hi there! I am Aria — your warm, engaging, and expressive voice."
}

class TTSEngine:
    def __init__(self, voice_key: str = DEFAULT_VOICE, mode_key: str = DEFAULT_VOICE_MODE, effect_key: str = DEFAULT_AUDIO_EFFECT):
        if voice_key not in VOICES:
            voice_key = DEFAULT_VOICE
        self.voice_info = VOICES[voice_key]
        self.voice_id = self.voice_info["id"]

        mode_data = VOICE_MODES.get(mode_key, VOICE_MODES[DEFAULT_VOICE_MODE])
        self.rate = mode_data.get("rate", "+12%")
        self.pitch = mode_data.get("pitch", "-1Hz")

        if effect_key not in AUDIO_EFFECTS:
            effect_key = DEFAULT_AUDIO_EFFECT
        self.effect_key = effect_key
        self.dsp_filter = AUDIO_EFFECTS[self.effect_key]["filter"]

    @classmethod
    async def generate_voice_demo(cls, voice_key: str, output_path: str) -> str:
        """Tanlangan diktor uchun 2.5 soniyalik audio namuna yaratish yoki keshdan olish."""
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            return output_path

        voice_data = VOICES.get(voice_key, VOICES[DEFAULT_VOICE])
        voice_id = voice_data["id"]
        demo_text = VOICE_DEMO_TEXTS.get(voice_key, "Salom! Bu ovoz namunasi.")

        clean_text = transliterate_uzbek(demo_text) if voice_data.get("lang") == "uz" else demo_text
        temp_raw = output_path + ".demo.raw.mp3"
        comm = edge_tts.Communicate(clean_text, voice_id, rate="+8%", pitch="0Hz")
        await comm.save(temp_raw)

        dsp_filter = (
            "highpass=f=80,"
            "equalizer=f=220:t=q:w=1.2:g=2.5,"
            "equalizer=f=3600:t=q:w=1.0:g=3.0,"
            "compand=attacks=0.02:decays=0.1:points=-80/-80|-25/-15|-10/-5|0/0:soft-knee=6,"
            "loudnorm=I=-16:TP=-1.5:LRA=11"
        )
        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-i", temp_raw,
            "-af", dsp_filter,
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            output_path
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=20)
        except Exception:
            cmd_fb = ["ffmpeg", "-nostdin", "-y", "-i", temp_raw, "-c:a", "libmp3lame", "-b:a", "128k", output_path]
            subprocess.run(cmd_fb, capture_output=True, check=True, timeout=20)
        finally:
            if os.path.exists(temp_raw):
                try: os.remove(temp_raw)
                except Exception: pass

        return output_path

    async def generate_scene_audio(
        self,
        text: str,
        output_path: str,
        speaker: int = 1,
        is_hook: bool = False,
        is_climax: bool = False
    ) -> float:
        """
        Bitta kadr matnini ovozlashtiradi, Studiya DSP filtri va EBU R128 bilan boyitadi va saqlaydi.
        Agar speaker == 2 bo'lsa, avtomatik ravishda qarama-qarshi jinsdagi hamroh ovoziga o'tadi!
        is_hook (1-kadr) uchun baquvvat ritm (+16%), is_climax (yakun) uchun chuqur basli (-2Hz) modulyatsiya.
        """
        chosen_voice_id = self.voice_id
        if speaker == 2:
            partner_map = {
                "uz-UZ-SardorNeural": "uz-UZ-MadinaNeural",
                "uz-UZ-MadinaNeural": "uz-UZ-SardorNeural",
                "ru-RU-DmitryNeural": "ru-RU-SvetlanaNeural",
                "ru-RU-SvetlanaNeural": "ru-RU-DmitryNeural",
                "en-US-ChristopherNeural": "en-US-AriaNeural",
                "en-US-AriaNeural": "en-US-ChristopherNeural"
            }
            chosen_voice_id = partner_map.get(self.voice_id, self.voice_id)

        clean_text = transliterate_uzbek(text) if self.voice_info.get("lang") == "uz" else text

        rate_val = self.rate
        pitch_val = self.pitch
        if is_hook:
            rate_val = "+16%"
            pitch_val = "+1Hz"
        elif is_climax:
            rate_val = "+4%"
            pitch_val = "-2Hz"

        temp_raw = output_path + ".raw.mp3"
        comm = edge_tts.Communicate(clean_text, chosen_voice_id, rate=rate_val, pitch=pitch_val)
        await comm.save(temp_raw)

        # Studiya Broadcast DSP zanjiri (Tanlangan DSP profili bo'yicha)
        dsp_filter = self.dsp_filter
        if "loudnorm" in dsp_filter and "afade" not in dsp_filter:
            dsp_filter = dsp_filter.replace("loudnorm", "afade=t=in:st=0:d=0.018,loudnorm")

        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-i", temp_raw,
            "-af", dsp_filter,
            "-c:a", "pcm_s16le",
            "-ar", "44100",
            output_path
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=30)
        except Exception as e:
            # Fallback
            cmd_fb = ["ffmpeg", "-nostdin", "-y", "-i", temp_raw, "-c:a", "pcm_s16le", "-ar", "44100", output_path]
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
            return 4.0

    def build_word_timings(self, text: str, start_offset: float, total_duration: float) -> List[Dict]:
        """
        Bo'g'inlar va tinish belgilari akustikasiga asoslangan millisekundlik vaqt hisoblagich.
        """
        words = text.strip().split()
        if not words:
            return []

        vowels = set("aeiouyаеёиоуыэюяo'g'")
        
        # Har bir so'zning bo'g'in og'irligi
        word_weights = []
        for w in words:
            w_clean = w.lower()
            syllables = sum(1 for c in w_clean if c in vowels)
            weight = max(1.0, syllables * 1.6 + len(w_clean) * 0.35)
            word_weights.append(weight)

        total_weight = sum(word_weights)

        # Nafas va ulanish pauzalari
        lead_pad = min(0.08, total_duration * 0.02)
        tail_pad = min(0.10, total_duration * 0.03)
        active_duration = max(0.4, total_duration - lead_pad - tail_pad)

        word_timings = []
        current_time = start_offset + lead_pad

        for i, word in enumerate(words):
            fraction = word_weights[i] / total_weight
            base_dur = active_duration * fraction

            # Tinish belgilariga qarab silliq pauza
            extra_pause = 0.0
            if word.endswith((",", ";", "-")):
                extra_pause = min(0.12, base_dur * 0.22)
            elif word.endswith((".", "!", "?", ":")):
                extra_pause = min(0.22, base_dur * 0.32)

            actual_word_dur = max(0.16, base_dur - extra_pause)
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
        """
        Barcha kadrlarni parallel oqimda (Concurrent Async) tezkor ovozlashtiradi
        va vaqt chizig'i (Global Timeline) bo'yicha tartiblaydi.
        """
        total_sc = len(scenes)
        tasks = []
        for i, sc in enumerate(scenes):
            scene_idx = i + 1
            audio_path = str(TEMP_DIR / f"{task_id}_audio_{scene_idx}.wav")
            speaker_id = sc.get("speaker", 1)
            is_hook = (i == 0)
            is_climax = (i == total_sc - 1 and total_sc > 1)
            tasks.append(
                self.generate_scene_audio(
                    sc["text"],
                    audio_path,
                    speaker=speaker_id,
                    is_hook=is_hook,
                    is_climax=is_climax
                )
            )

        durations = await asyncio.gather(*tasks)

        processed_scenes = []
        global_timeline_offset = 0.0

        for i, sc in enumerate(scenes):
            scene_idx = i + 1
            audio_path = str(TEMP_DIR / f"{task_id}_audio_{scene_idx}.wav")
            dur = durations[i]
            speaker_id = sc.get("speaker", 1)
            timed_words = self.build_word_timings(sc["text"], global_timeline_offset, dur)

            scene_record = {
                "scene_num": scene_idx,
                "speaker": speaker_id,
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
