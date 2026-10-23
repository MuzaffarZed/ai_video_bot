import os, sys, unittest, tempfile
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, r'C:\Users\MuzaffarZed\ai_workspace\ai_video_bot')

from config import (
    VOICES, VIDEO_STYLES, VISUAL_FILTERS, SUBTITLE_THEMES, SUBTITLE_SIZES,
    FORMATS, DURATIONS, MUSIC_GENRES, ART_STYLES, TEMP_DIR
)
from script_generator import ScriptGenerator
from visual_engine import VisualEngine
from tts_engine import TTSEngine
from subtitle_engine import SubtitleEngine
from audio_mixer import AudioMixer
from video_engine import VideoEngine
from pipeline import VideoPipeline

class TestSingularity8(unittest.TestCase):
    def test_config_integrity(self):
        self.assertIn("uz_sardor", VOICES)
        self.assertIn("photoreal", ART_STYLES)
        self.assertIn("suspense_drama", MUSIC_GENRES)
        self.assertIn("lofi_vibes", MUSIC_GENRES)
        self.assertIn("9:16", FORMATS)
        self.assertIn("teal_orange", VISUAL_FILTERS)

    def test_script_generator_procedural_and_ideas(self):
        sg = ScriptGenerator()
        # Test procedural
        scenes_uz = sg._generate_procedural("Qora tuynuklar", "uz", "top_facts", 3)
        self.assertEqual(len(scenes_uz), 3)
        self.assertIn("text", scenes_uz[0])
        self.assertIn("visual_prompt", scenes_uz[0])

        # Test custom script parsing
        custom_txt = "Birinchi jumla\nIkkinchi jumla\nUchinchi jumla"
        parsed = sg.parse_custom_user_script(custom_txt, "Test")
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0]["text"], "Birinchi jumla")

        # Test trending ideas
        ideas = ScriptGenerator.generate_trending_ideas()
        self.assertTrue(len(ideas) >= 3)
        self.assertIn("title", ideas[0])

        # Test SEO
        seo = sg.generate_viral_seo_package("Koinot siri", "uz")
        self.assertIn("hashtags", seo)
        self.assertIn("#reels", seo["hashtags"])

    def test_visual_engine_categories_and_art(self):
        ve = VisualEngine("9:16")
        cat = ve.detect_category("koinot va galaktikalar")
        self.assertEqual(cat, "space")

        cat_biz = ve.detect_category("biznes va boylik sirlari")
        self.assertEqual(cat_biz, "business")

        genre = ve.get_music_genre_for_category("business")
        self.assertEqual(genre, "epic_inspiration")

        # Test offline graphic generation
        test_out = str(TEMP_DIR / "test_fallback.jpg")
        ve._generate_fallback_graphic("space", test_out)
        self.assertTrue(os.path.exists(test_out))
        self.assertTrue(os.path.getsize(test_out) > 1000)
        try: os.remove(test_out)
        except Exception: pass

    def test_tts_engine_timings(self):
        tts = TTSEngine()
        text = "Olamlar siri va buyuk koinot haqiqati"
        timings = tts.build_word_timings(text, start_offset=0.0, total_duration=4.0)
        self.assertEqual(len(timings), len(text.split()))
        self.assertGreater(timings[-1]["end"], timings[0]["start"])

    def test_subtitle_engine_ass_generation(self):
        se = SubtitleEngine()
        scenes = [{
            "scene_num": 1,
            "text": "Salom dunyo",
            "start_time": 0.0,
            "end_time": 3.0,
            "words": [
                {"word": "Salom", "start": 0.1, "end": 1.2},
                {"word": "dunyo", "start": 1.3, "end": 2.8}
            ]
        }]
        test_ass = str(TEMP_DIR / "test_subs.ass")
        se.generate_ass(scenes, test_ass, theme_key="gold", format_key="9:16")
        self.assertTrue(os.path.exists(test_ass))
        with open(test_ass, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("[Script Info]", content)
            self.assertIn("Karaoke", content)
            self.assertIn("Dasturchi: MuzaffarZed", content)
        try: os.remove(test_ass)
        except Exception: pass

    def test_audio_mixer_track_synthesis(self):
        mixer = AudioMixer()
        for g in ["suspense_drama", "lofi_vibes"]:
            test_wav = str(TEMP_DIR / f"test_{g}.wav")
            mixer._synthesize_track(g, test_wav, duration=1.0)
            self.assertTrue(os.path.exists(test_wav))
            self.assertTrue(os.path.getsize(test_wav) > 1000)
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
