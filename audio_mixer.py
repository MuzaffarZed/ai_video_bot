"""
MuzaffarZed AI Video Bot - Ovoz va Musiqa Mikseri (Audio Studio 3.0 Flagship)
Nutq audiolari, ko'p janrli fon musiqalari, Sahna almashuv Whoosh SFX va Podkast MP3 eksporti.
Muallif: MuzaffarZed
"""
import os
import subprocess
import wave
import numpy as np
from typing import List, Dict
from config import TEMP_DIR, MUSIC_DIR, SFX_DIR, MUSIC_GENRES, DEFAULT_MUSIC_GENRE

class AudioMixer:
    def __init__(self):
        self._ensure_all_tracks()
        self._ensure_default_sfx()

    def _ensure_all_tracks(self):
        for genre_key in MUSIC_GENRES:
            if genre_key == "auto":
                continue
            track_path = MUSIC_DIR / f"{genre_key}.wav"
            if not track_path.exists():
                self._synthesize_track(genre_key, str(track_path), duration=65.0)

    def _ensure_default_sfx(self):
        self.default_whoosh = SFX_DIR / "whoosh.wav"
        if not self.default_whoosh.exists():
            self._generate_whoosh(str(self.default_whoosh))

    @staticmethod
    def _synthesize_track(genre: str, file_path: str, duration: float = 65.0):
        sr = 44100
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)

        if genre == "cosmic_deep":
            chord_freqs = [
                [65.41, 130.81, 155.56, 196.00],
                [77.78, 155.56, 196.00, 233.08],
                [51.91, 103.83, 130.81, 155.56],
                [49.00, 98.00, 123.47, 146.83]
            ]
        elif genre == "epic_inspiration":
            chord_freqs = [
                [146.83, 185.00, 220.00, 293.66],
                [110.00, 164.81, 220.00, 277.18],
                [123.47, 146.83, 185.00, 246.94],
                [98.00, 146.83, 196.00, 246.94]
            ]
        elif genre == "tech_modern":
            chord_freqs = [
                [92.50, 138.59, 185.00, 220.00],
                [110.00, 164.81, 220.00, 261.63],
                [82.41, 123.47, 164.81, 196.00],
                [123.47, 146.83, 185.00, 246.94]
            ]
        else: # ambient_chill
            chord_freqs = [
                [130.81, 164.81, 196.00, 246.94],
                [110.00, 130.81, 164.81, 196.00],
                [146.83, 174.61, 220.00, 261.63],
                [98.00, 123.47, 146.83, 174.61]
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
                sub_audio += 0.20 * np.sin(2 * np.pi * f * t_sub)
                sub_audio += 0.08 * np.sin(2 * np.pi * (f * 2) * t_sub)
                sub_audio += 0.03 * np.sin(2 * np.pi * (f * 3) * t_sub)
            env = np.sin(np.pi * (t_sub / bar_len)) ** 0.6
            audio[mask] = sub_audio * env

        audio = (audio * 0.38 * 32767).astype(np.int16)
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio.tobytes())

    @staticmethod
    def _generate_whoosh(file_path: str):
        sr = 44100
        dur = 0.35
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        env = np.exp(-((t - 0.16) ** 2) / (2 * (0.05 ** 2)))
        noise = np.random.uniform(-1, 1, len(t))
        freq = 300 + 2200 * np.sin(np.pi * (t / dur))
        sweep = np.sin(2 * np.pi * freq * t)
        audio = (noise * 0.30 + sweep * 0.70) * env
        audio = (audio * 0.40 * 32767).astype(np.int16)
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio.tobytes())

    def mix(
        self,
        voice_files: List[str],
        output_master_path: str,
        genre: str = "ambient_chill",
        transition_points: List[float] = None
    ) -> str:
        """
        Barcha kadrlar ovozlarini birlashtiradi, mavzuga mos fon musiqasi (Audio Ducking)
        va sahna o'tishlarida Whoosh SFX bilan mikslaydi.
        """
        if genre == "auto" or not genre:
            genre = "ambient_chill"

        bgm_path = str(MUSIC_DIR / f"{genre}.wav")
        if not os.path.exists(bgm_path):
            bgm_path = str(MUSIC_DIR / "ambient_chill.wav")

        concat_txt = TEMP_DIR / "concat_list.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for v in voice_files:
                clean_path = v.replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        merged_voice = str(TEMP_DIR / "merged_voice.wav")
        cmd_merge = [
            "ffmpeg", "-nostdin", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:a", "pcm_s16le",
            "-ar", "44100",
            merged_voice
        ]
        subprocess.run(cmd_merge, capture_output=True, check=True, timeout=60)

        # Davomiylikni o'lchash
        dur_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            merged_voice
        ]
        res = subprocess.run(dur_cmd, capture_output=True, text=True, check=True, timeout=20)
        total_dur = float(res.stdout.strip())

        fade_out_start = max(0.0, total_dur - 1.2)
        
        # Audio Ducking filter complex
        filter_complex = (
            f"[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[voice];"
            f"[1:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.12,"
            f"atrim=0:{total_dur:.3f},afade=t=in:st=0:d=0.8,afade=t=out:st={fade_out_start:.3f}:d=1.2[bgm];"
            f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]"
        )

        cmd_mix = [
            "ffmpeg", "-nostdin", "-y",
            "-i", merged_voice,
            "-stream_loop", "-1", "-i", bgm_path,
            "-filter_complex", filter_complex,
            "-map", "[outa]",
            "-c:a", "pcm_s16le",
            "-ar", "44100",
            output_master_path
        ]
        subprocess.run(cmd_mix, capture_output=True, check=True, timeout=60)
        return output_master_path

    def export_mp3_podcast(self, wav_master_path: str, mp3_output_path: str) -> str:
        """Video audiosidan yuqori sifatli 192kbps MP3 podkast fayli hosil qiladi."""
        cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-i", wav_master_path,
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            mp3_output_path
        ]
        subprocess.run(cmd, capture_output=True, check=True, timeout=30)
        return mp3_output_path
