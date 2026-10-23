"""
MuzaffarZed AI Video Bot - CLI Sinov va Tezkor Generatsiya
Terminal orqali darhol 1-bosishda Full HD video yaratish vositasi.
Muallif: MuzaffarZed
"""
import os
import sys
import argparse
import asyncio
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from pathlib import Path

current_dir = str(Path(__file__).resolve().parent)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from pipeline import VideoPipeline
from config import VOICES, DEFAULT_VOICE, VOICE_MODES, DEFAULT_VOICE_MODE

async def main():
    parser = argparse.ArgumentParser(description="MuzaffarZed AI Video Generator CLI")
    parser.add_argument("--topic", type=str, default="Koinotning eng sirli hodisasi: Qora tuynuklar", help="Video mavzusi")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, choices=list(VOICES.keys()), help="Ovoz tanlovi")
    parser.add_argument("--mode", type=str, default=DEFAULT_VOICE_MODE, choices=list(VOICE_MODES.keys()), help="Ovoz rejimi")
    args = parser.parse_args()

    print("=" * 65)
    print("🎬 MUZAFFARZED AI VIDEO CREATOR - ISHGA TUSHDI")
    print(f"📌 Mavzu: {args.topic}")
    print(f"🎙 Ovoz:  {VOICES[args.voice]['name']}")
    print(f"⚡ Rejim: {VOICE_MODES[args.mode]['name']}")
    print("=" * 65)

    start_time = time.time()

    async def on_progress(step, total, msg):
        print(f"\n[Qadam {step}/{total}] -> {msg}")

    pipeline = VideoPipeline()
    result = await pipeline.create_video(
        topic=args.topic,
        voice_key=args.voice,
        voice_mode=args.mode,
        progress_callback=on_progress
    )

    elapsed = time.time() - start_time
    video_path = result["video_path"]
    size_mb = os.path.getsize(video_path) / (1024 * 1024)

    print("\n" + "=" * 65)
    print("✨ VIDEO MUVAFFAQIYATLI YARATILDI! (Zero-Defect Standard)")
    print(f"📂 Fayl:         {video_path}")
    print(f"⏱ Davomiyligi:  {result['duration']:.2f} soniya")
    print(f"💾 Hajmi:        {size_mb:.2f} MB")
    print(f"⚡ Tayyorlandi:  {elapsed:.2f} soniyada")
    print("Muallif: Dasturchi MuzaffarZed")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(main())
