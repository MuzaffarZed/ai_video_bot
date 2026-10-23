"""
MuzaffarZed AI Video Bot - Ovoz va Musiqa Mikseri
Nutq audiolari va fon musiqasini uyg'unlashtirish (Audio Ducking bilan).
Muallif: MuzaffarZed
"""
import os
import subprocess
import wave
import numpy as np
from typing import List
from config import TEMP_DIR, MUSIC_DIR

class AudioMixer:
    def __init__(self):
        self._ensure_default_bgm()

    def _ensure_default_bgm(self):
        self.default_bgm = MUSIC_DIR / "ambient_chill.wav"
        if not self.default_bgm.exists():
            self._generate_ambient_track(str(self.default_bgm), duration=45.0)

    @staticmethod
    def _generate_ambient_track(file_path: str, duration: float = 45.0):
        sr = 44100
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        
        chord_freqs = [
            [130.81, 164.81, 196.00, 246.94], # Cmaj7
            [110.00, 130.81, 164.81, 196.00], # Am7
            [146.83, 174.61, 220.00, 261.63], # Dm7
            [98.00, 123.47, 146.83, 174.61]   # G7
        ]
        
        audio = np.zeros_like(t)
        bar_len = duration / len(chord_freqs)
        
        for i, chord in enumerate(chord_freqs):
            t_start = i * bar_len
            t_end = (i + 1) * bar_len
            mask = (t >= t_start) & (t < t_end)
            t_sub = t[mask] - t_start
            
            sub_audio = np.zeros_like(t_sub)
            for f in chord:
                sub_audio += 0.22 * np.sin(2 * np.pi * f * t_sub)
                sub_audio += 0.08 * np.sin(2 * np.pi * (f * 2) * t_sub)
                
            env = np.sin(np.pi * (t_sub / bar_len)) ** 0.5
            audio[mask] = sub_audio * env

        audio = (audio * 0.35 * 32767).astype(np.int16)

        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio.tobytes())

    def mix(self, voice_files: List[str], output_master_path: str, bgm_path: str = None) -> str:
        """
        Barcha kadrlar ovozlarini birlashtiradi va fon musiqasi bilan mikslaydi.
        """
        if not bgm_path or not os.path.exists(bgm_path):
            bgm_path = str(self.default_bgm)

        # 1. Concat ro'yxatini tuzish
        concat_txt = TEMP_DIR / "concat_list.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for v in voice_files:
                clean_path = v.replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        merged_voice = str(TEMP_DIR / "merged_voice.wav")
        cmd_merge = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:a", "pcm_s16le",
            merged_voice
        ]
        subprocess.run(cmd_merge, capture_output=True, check=True)

        # Ovoz davomiyligini aniqlash
        dur_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            merged_voice
        ]
        res = subprocess.run(dur_cmd, capture_output=True, text=True, check=True)
        total_dur = float(res.stdout.strip())

        # 2. BGM bilan mikserlash (resample + audio ducking)
        fade_out_start = max(0.0, total_dur - 1.2)
        filter_complex = (
            f"[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[voice];"
            f"[1:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.12,"
            f"atrim=0:{total_dur:.3f},afade=t=in:st=0:d=0.8,afade=t=out:st={fade_out_start:.3f}:d=1.2[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]"
        )

        # Standart WAV pcm_s16le chiqaramiz, shunda hech qanday kodek mojaro bo'lmaydi
        cmd_mix = [
            "ffmpeg", "-y",
            "-i", merged_voice,
            "-stream_loop", "-1", "-i", bgm_path,
            "-filter_complex", filter_complex,
            "-map", "[outa]",
            "-c:a", "pcm_s16le",
            output_master_path
        ]
        subprocess.run(cmd_mix, capture_output=True, check=True)
        return output_master_path
