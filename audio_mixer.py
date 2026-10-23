"""
MuzaffarZed AI Video Bot - Ovoz va Musiqa Mikseri (Audio Studio 3.0 Flagship)
Nutq audiolari, ko'p janrli fon musiqalari, Sahna almashuv Whoosh SFX va Podkast MP3 eksporti.
Muallif: MuzaffarZed
"""
import os
import shutil
import subprocess
import wave
import numpy as np
from typing import List, Dict, Optional
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
        self.default_boom = SFX_DIR / "impact_boom.wav"
        if not self.default_boom.exists():
            self._generate_impact_boom(str(self.default_boom))
        self.default_shutter = SFX_DIR / "camera_shutter.wav"
        if not self.default_shutter.exists():
            self._generate_shutter(str(self.default_shutter))
        self.default_riser = SFX_DIR / "riser_sweep.wav"
        if not self.default_riser.exists():
            self._generate_riser(str(self.default_riser))
        self.default_chime = SFX_DIR / "outro_chime.wav"
        if not self.default_chime.exists():
            self._generate_outro_chime(str(self.default_chime))

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
        elif genre == "suspense_drama":
            chord_freqs = [
                [55.00, 77.78, 110.00, 155.56],
                [51.91, 73.42, 103.83, 146.83],
                [49.00, 69.30, 98.00, 138.59],
                [58.27, 82.41, 116.54, 164.81]
            ]
        elif genre == "lofi_vibes":
            chord_freqs = [
                [130.81, 164.81, 196.00, 246.94],
                [116.54, 146.83, 174.61, 220.00],
                [103.83, 130.81, 155.56, 196.00],
                [98.00, 123.47, 146.83, 185.00]
            ]
        elif genre == "cyber_action":
            chord_freqs = [
                [65.41, 130.81, 196.00, 261.63],
                [73.42, 146.83, 220.00, 293.66],
                [82.41, 164.81, 246.94, 329.63],
                [55.00, 110.00, 164.81, 220.00]
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

    @staticmethod
    def _generate_impact_boom(file_path: str):
        sr = 44100
        dur = 0.85
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        freq = 36.0 + 104.0 * np.exp(-t / 0.24)
        phase = 2 * np.pi * np.cumsum(freq) / sr
        sine_wave = np.sin(phase)
        click = np.random.uniform(-1, 1, len(t)) * np.exp(-t / 0.025)
        env = np.exp(-t / 0.28)
        audio = (sine_wave * 0.88 + click * 0.12) * env
        audio = (audio * 0.65 * 32767).astype(np.int16)
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio.tobytes())

    @staticmethod
    def _generate_shutter(file_path: str):
        sr = 44100
        dur = 0.25
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        click1 = np.random.uniform(-1, 1, len(t)) * np.exp(-((t - 0.04) ** 2) / (2 * (0.010 ** 2)))
        click2 = np.random.uniform(-1, 1, len(t)) * np.exp(-((t - 0.13) ** 2) / (2 * (0.012 ** 2)))
        audio = (click1 * 0.65 + click2 * 0.85)
        audio = (audio * 0.50 * 32767).astype(np.int16)
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio.tobytes())

    @staticmethod
    def _generate_riser(file_path: str):
        sr = 44100
        dur = 1.2
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        freq = 180.0 * (1200.0 / 180.0) ** (t / dur)
        phase = 2 * np.pi * np.cumsum(freq) / sr
        sweep = np.sin(phase)
        noise = np.random.uniform(-1, 1, len(t)) * (t / dur) ** 2
        env = (t / dur) ** 1.8
        audio = (sweep * 0.70 + noise * 0.30) * env
        audio = (audio * 0.42 * 32767).astype(np.int16)
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio.tobytes())

    @staticmethod
    def _generate_outro_chime(file_path: str):
        """Kristaldek tiniq, nafis yakuniy studiya chimesi (Outro sonic logo)."""
        sr = 44100
        dur = 1.6
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        sig = (
            0.40 * np.sin(2 * np.pi * 1318.5 * t) +
            0.30 * np.sin(2 * np.pi * 1661.2 * t) +
            0.20 * np.sin(2 * np.pi * 1975.5 * t) +
            0.15 * np.sin(2 * np.pi * 2637.0 * t)
        )
        env = np.exp(-3.2 * t)
        audio = (sig * env * 32767 * 0.40).astype(np.int16)
        with wave.open(file_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio.tobytes())

    def _build_sfx_track(self, transition_points: List[float], total_dur: float, sfx_output_path: str) -> bool:
        """
        Sahna o'tishlari uchun whoosh, boshlanish uchun cinematic impact boom,
        kulminatsiya oldidan riser sweep va yakun uchun outro chime SFX yo'lagini yaratadi.
        """
        sr = 44100
        total_samples = int(sr * total_dur)
        if total_samples <= 0:
            return False

        sfx_track = np.zeros(total_samples, dtype=np.float32)

        # 1. 0.0s da Cinematic Hook Impact Boom
        if self.default_boom.exists():
            try:
                with wave.open(str(self.default_boom), 'r') as wf:
                    boom_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
                add_len = min(len(boom_data), total_samples)
                sfx_track[:add_len] += boom_data[:add_len] * 0.38
            except Exception as e:
                print(f"[SFX Boom Notice] {e}")

        # 2. Sahna o'tishlarida Whoosh SFX
        if transition_points and self.default_whoosh.exists():
            try:
                with wave.open(str(self.default_whoosh), 'r') as wf:
                    whoosh_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
                whoosh_len = len(whoosh_data)
                half_whoosh = int(sr * 0.14)

                for tp in transition_points:
                    st_sample = int(tp * sr) - half_whoosh
                    if st_sample < 0:
                        st_sample = 0
                    end_sample = min(st_sample + whoosh_len, total_samples)
                    actual_len = end_sample - st_sample
                    if actual_len > 0:
                        sfx_track[st_sample:end_sample] += whoosh_data[:actual_len] * 0.28
            except Exception as e:
                print(f"[SFX Whoosh Notice] {e}")

        # 3. Yakuniy kadr (Climax) oldidan kinematik Riser Swell FX
        if transition_points and len(transition_points) >= 1 and self.default_riser.exists():
            try:
                climax_point = transition_points[-1]
                with wave.open(str(self.default_riser), 'r') as wf:
                    riser_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
                riser_len = len(riser_data)
                riser_start = int(climax_point * sr) - riser_len
                if riser_start >= 0 and riser_start + riser_len <= total_samples:
                    sfx_track[riser_start:riser_start + riser_len] += riser_data * 0.30
            except Exception as e:
                print(f"[SFX Riser Notice] {e}")

        # 4. Outro CTA yakunida kristal Outro Chime SFX
        if total_dur >= 3.0 and self.default_chime.exists():
            try:
                with wave.open(str(self.default_chime), 'r') as wf:
                    chime_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32767.0
                chime_len = len(chime_data)
                chime_start = max(0, total_samples - int(sr * 1.5))
                end_chime = min(chime_start + chime_len, total_samples)
                actual_chime_len = end_chime - chime_start
                if actual_chime_len > 0:
                    sfx_track[chime_start:end_chime] += chime_data[:actual_chime_len] * 0.28
            except Exception as e:
                print(f"[SFX Outro Notice] {e}")

        np.clip(sfx_track, -1.0, 1.0, out=sfx_track)
        audio_int16 = (sfx_track * 32767).astype(np.int16)

        with wave.open(sfx_output_path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio_int16.tobytes())

        return True

    def mix(
        self,
        voice_files: List[str],
        output_master_path: str,
        genre: str = "ambient_chill",
        transition_points: List[float] = None,
        bgm_volume: float = 0.15,
        output_vocals_path: Optional[str] = None
    ) -> str:
        """
        Barcha kadrlar ovozlarini birlashtiradi, mavzuga mos fon musiqasi (Audio Ducking)
        va sahna o'tishlarida Whoosh SFX bilan mikslaydi.
        Agar bgm_volume <= 0.001 bo'lsa, musiqasiz faqat toza nutq chiqaradi.
        """
        if genre == "auto" or not genre:
            genre = "ambient_chill"

        bgm_path = str(MUSIC_DIR / f"{genre}.wav")
        if not os.path.exists(bgm_path):
            bgm_path = str(MUSIC_DIR / "ambient_chill.wav")

        task_tag = os.path.splitext(os.path.basename(output_master_path))[0]
        concat_txt = TEMP_DIR / f"concat_list_{task_tag}.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for v in voice_files:
                clean_path = v.replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        merged_voice = str(TEMP_DIR / f"merged_voice_{task_tag}.wav")
        cmd_merge = [
            "ffmpeg", "-nostdin", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:a", "pcm_s16le",
            "-ar", "44100",
            merged_voice
        ]
        try:
            subprocess.run(cmd_merge, capture_output=True, check=True, timeout=60)
            if output_vocals_path:
                try:
                    shutil.copyfile(merged_voice, output_vocals_path)
                except Exception as cp_err:
                    print(f"[Vocals Copy Notice] {cp_err}")
        finally:
            if os.path.exists(concat_txt):
                try: os.remove(concat_txt)
                except Exception: pass

        # Davomiylikni o'lchash
        dur_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            merged_voice
        ]
        res = subprocess.run(dur_cmd, capture_output=True, text=True, check=True, timeout=20)
        total_dur = float(res.stdout.strip())

        # SFX yo'lagi (Cinematic Hook Boom + Scene Transition Whoosh)
        sfx_path = str(TEMP_DIR / f"sfx_layer_{os.path.basename(output_master_path)}.wav")
        has_sfx = self._build_sfx_track(transition_points or [], total_dur, sfx_path)

        fade_out_start = max(0.0, total_dur - 1.2)

        # Agar musiqasiz rejim tanlangan bo'lsa
        if bgm_volume <= 0.001 or genre == "mute":
            if has_sfx and os.path.exists(sfx_path):
                filter_complex = (
                    f"[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[voice];"
                    f"[1:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[sfx];"
                    f"[voice][sfx]amix=inputs=2:duration=first:dropout_transition=2[outa]"
                )
                cmd_mix = [
                    "ffmpeg", "-nostdin", "-y",
                    "-i", merged_voice,
                    "-i", sfx_path,
                    "-filter_complex", filter_complex,
                    "-map", "[outa]",
                    "-c:a", "pcm_s16le",
                    "-ar", "44100",
                    output_master_path
                ]
            else:
                cmd_mix = [
                    "ffmpeg", "-nostdin", "-y",
                    "-i", merged_voice,
                    "-c:a", "pcm_s16le",
                    "-ar", "44100",
                    output_master_path
                ]
            subprocess.run(cmd_mix, capture_output=True, check=True, timeout=60)
            return output_master_path

        # Audio Ducking va SFX miks
        if has_sfx and os.path.exists(sfx_path):
            filter_complex = (
                f"[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[voice];"
                f"[1:a]aresample=44100,aformat=channel_layouts=stereo,volume={bgm_volume:.3f},"
                f"atrim=0:{total_dur:.3f},afade=t=in:st=0:d=0.8,afade=t=out:st={fade_out_start:.3f}:d=1.2[bgm];"
                f"[2:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[sfx];"
                f"[voice][bgm][sfx]amix=inputs=3:duration=first:dropout_transition=2[outa]"
            )
            cmd_mix = [
                "ffmpeg", "-nostdin", "-y",
                "-i", merged_voice,
                "-stream_loop", "-1", "-i", bgm_path,
                "-i", sfx_path,
                "-filter_complex", filter_complex,
                "-map", "[outa]",
                "-c:a", "pcm_s16le",
                "-ar", "44100",
                output_master_path
            ]
        else:
            filter_complex = (
                f"[0:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.0[voice];"
                f"[1:a]aresample=44100,aformat=channel_layouts=stereo,volume={bgm_volume:.3f},"
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
