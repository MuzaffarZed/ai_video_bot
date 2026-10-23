import os, sys, unittest
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, r'C:\Users\MuzaffarZed\ai_workspace\ai_video_bot')

from config import (
    VOICES, VIDEO_STYLES, VISUAL_FILTERS, SUBTITLE_THEMES, SUBTITLE_SIZES,
    FORMATS, DURATIONS, MUSIC_GENRES, ART_STYLES, STUDIO_PRESETS, MUSIC_VOLUMES, TEMP_DIR
)
from script_generator import ScriptGenerator, transliterate_uzbek
from visual_engine import VisualEngine
from tts_engine import TTSEngine
from subtitle_engine import SubtitleEngine
from audio_mixer import AudioMixer
from video_engine import VideoEngine
from pipeline import VideoPipeline

class TestSingularity10(unittest.TestCase):
    def test_config_integrity(self):
        self.assertIn("uz_sardor", VOICES)
        self.assertIn("photoreal", ART_STYLES)
        self.assertIn("suspense_drama", MUSIC_GENRES)
        self.assertIn("lofi_vibes", MUSIC_GENRES)
        self.assertIn("podcast_dialogue", VIDEO_STYLES)
        self.assertIn("tiktok_hook", STUDIO_PRESETS)
        self.assertIn("mute", MUSIC_VOLUMES)
        self.assertIn("9:16", FORMATS)
        self.assertIn("teal_orange", VISUAL_FILTERS)

    def test_transliterate_uzbek(self):
        cyrillic = "Қора туйнуклар ва ҳаёт сирлари"
        latin = transliterate_uzbek(cyrillic)
        self.assertEqual(latin, "Qora tuynuklar va hayot sirlari")
        self.assertEqual(transliterate_uzbek("Ўзбекистон"), "O'zbekiston")
        self.assertEqual(transliterate_uzbek("Ғалаба"), "G'alaba")

    def test_script_generator_podcast_dialogue(self):
        sg = ScriptGenerator()
        scenes = sg._generate_procedural("Koinot siri", "uz", "podcast_dialogue", 3)
        self.assertEqual(len(scenes), 3)
        self.assertEqual(scenes[0]["speaker"], 1)
        self.assertEqual(scenes[1]["speaker"], 2)
        self.assertEqual(scenes[2]["speaker"], 1)

    def test_visual_engine_smart_blur_padding(self):
        ve = VisualEngine("9:16")
        # Create a horizontal (16:9) image to test blur padding
        test_in = str(TEMP_DIR / "test_landscape.jpg")
        img = Image.new("RGB", (800, 450), color=(100, 150, 200))
        img.save(test_in, "JPEG")

        test_out = str(TEMP_DIR / "test_padded.jpg")
        ve.process_custom_user_image(test_in, test_out)
        self.assertTrue(os.path.exists(test_out))
        with Image.open(test_out) as out_im:
            self.assertEqual(out_im.width, 1080)
            self.assertEqual(out_im.height, 1920)

        # Test thumbnail
        test_thumb = str(TEMP_DIR / "test_thumb.jpg")
        ve.generate_thumbnail_card(test_out, "Test Title", test_thumb)
        self.assertTrue(os.path.exists(test_thumb))

        try:
            os.remove(test_in)
            os.remove(test_out)
            os.remove(test_thumb)
        except Exception:
            pass

    def test_subtitle_engine_srt_generation(self):
        se = SubtitleEngine()
        scenes = [{
            "scene_num": 1,
            "speaker": 1,
            "text": "Salom dunyo",
            "start_time": 0.0,
            "end_time": 3.0,
            "words": [
                {"word": "Salom", "start": 0.1, "end": 1.2},
                {"word": "dunyo", "start": 1.3, "end": 2.8}
            ]
        }]
        test_srt = str(TEMP_DIR / "test_subs.srt")
        se.generate_srt(scenes, test_srt)
        self.assertTrue(os.path.exists(test_srt))
        with open(test_srt, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("-->", content)
            self.assertIn("Salom dunyo", content)
        try: os.remove(test_srt)
        except Exception: pass

    def test_audio_mixer_track_synthesis(self):
        mixer = AudioMixer()
        for g in ["suspense_drama", "lofi_vibes"]:
            test_wav = str(TEMP_DIR / f"test_{g}.wav")
            mixer._synthesize_track(g, test_wav, duration=0.5)
            self.assertTrue(os.path.exists(test_wav))
            try: os.remove(test_wav)
            except Exception: pass

    def test_pipeline_attributes(self):
        pipeline = VideoPipeline()
        self.assertIsNotNone(pipeline.script_gen)
        self.assertIsNotNone(pipeline.audio_mixer)
        self.assertIsNotNone(pipeline.subtitle_eng)
        self.assertIsNotNone(pipeline.video_eng)
        self.assertIsNotNone(pipeline.visual_eng)

if __name__ == "__main__":
    unittest.main()
