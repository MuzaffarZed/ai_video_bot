import os, sys, time, unittest
from PIL import Image
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, r'C:\Users\MuzaffarZed\ai_workspace\ai_video_bot')

from config import (
    VOICES, VIDEO_STYLES, VISUAL_FILTERS, SUBTITLE_THEMES, SUBTITLE_SIZES,
    FORMATS, DURATIONS, MUSIC_GENRES, ART_STYLES, STUDIO_PRESETS, MUSIC_VOLUMES,
    CAMERA_MOTIONS, DEFAULT_CAMERA_MOTION, AUDIO_EFFECTS, DEFAULT_AUDIO_EFFECT,
    VOICE_MODES, DEFAULT_VOICE_MODE, TEMP_DIR, USER_UPLOADS_DIR
)
from script_generator import (
    ScriptGenerator, transliterate_uzbek, phonetic_uzbek_normalize,
    uzbek_number_to_words, to_uzbek_ordinal
)
from visual_engine import VisualEngine
from tts_engine import TTSEngine
from subtitle_engine import SubtitleEngine
from audio_mixer import AudioMixer
from video_engine import VideoEngine
from pipeline import VideoPipeline
from bot import extract_title_from_url, get_main_keyboard

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
        for g in ["suspense_drama", "lofi_vibes", "cyber_action"]:
            test_wav = str(TEMP_DIR / f"test_{g}.wav")
            mixer._synthesize_track(g, test_wav, duration=0.5)
            self.assertTrue(os.path.exists(test_wav))
            try: os.remove(test_wav)
            except Exception: pass

    def test_visual_engine_cover_poster(self):
        ve = VisualEngine("9:16")
        test_in = str(TEMP_DIR / "test_poster_in.jpg")
        img = Image.new("RGB", (1080, 1920), color=(30, 40, 60))
        img.save(test_in, "JPEG")

        test_poster = str(TEMP_DIR / "test_poster_out.jpg")
        ve.generate_cover_poster(test_in, "Epic Topic", test_poster)
        self.assertTrue(os.path.exists(test_poster))
        with Image.open(test_poster) as p_im:
            self.assertEqual(p_im.width, 1080)
            self.assertEqual(p_im.height, 1920)

        try:
            os.remove(test_in)
            os.remove(test_poster)
        except Exception:
            pass

    def test_camera_motions_and_sfx(self):
        self.assertIn("dynamic_drift", CAMERA_MOTIONS)
        self.assertIn("rapid_punch", CAMERA_MOTIONS)
        self.assertIn("static_crisp", CAMERA_MOTIONS)
        self.assertEqual(DEFAULT_CAMERA_MOTION, "dynamic_drift")

        mixer = AudioMixer()
        self.assertTrue(mixer.default_boom.exists())
        self.assertTrue(mixer.default_shutter.exists())
        self.assertTrue(mixer.default_whoosh.exists())
        self.assertTrue(mixer.default_riser.exists())

        test_sfx = str(TEMP_DIR / "test_sfx_track.wav")
        built = mixer._build_sfx_track([1.5, 3.0], 4.0, test_sfx)
        self.assertTrue(built)
        self.assertTrue(os.path.exists(test_sfx))
        try: os.remove(test_sfx)
        except Exception: pass

    def test_smart_category_soundtrack(self):
        ve = VisualEngine()
        self.assertEqual(ve.get_music_genre_for_category("ai"), "cyber_action")
        self.assertEqual(ve.get_music_genre_for_category("nature"), "lofi_vibes")
        self.assertEqual(ve.get_music_genre_for_category("space"), "cosmic_deep")

    def test_fast_reformat_validation(self):
        self.assertFalse(VideoPipeline.can_fast_reformat([], "non_existent.wav"))

    def test_script_translation(self):
        sg = ScriptGenerator()
        scenes = [
            {"scene_num": 1, "text": "Koinot cheksizdir", "visual_prompt": "space"},
            {"scene_num": 2, "text": "Yulduzlar porlaydi", "visual_prompt": "stars"}
        ]
        # Test translation structure
        res = sg.translate_script(scenes, "uz")
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]["scene_num"], 1)

    def test_video_engine_waveform_method(self):
        ve = VideoEngine()
        self.assertTrue(hasattr(ve, "render_voice_waveform_video"))

    def test_expand_user_prompt(self):
        exp_uz = ScriptGenerator.expand_user_prompt("Mars", "uz")
        self.assertIn("Mars", exp_uz)
        self.assertTrue(len(exp_uz) > 15)

        exp_pul = ScriptGenerator.expand_user_prompt("pul", "uz")
        self.assertIn("pul", exp_pul.lower())

    def test_subtitle_power_words(self):
        self.assertTrue(SubtitleEngine._is_power_word("pul"))
        self.assertTrue(SubtitleEngine._is_power_word("99%"))
        self.assertTrue(SubtitleEngine._is_power_word("million"))
        self.assertTrue(SubtitleEngine._is_power_word("koinot!"))
        self.assertFalse(SubtitleEngine._is_power_word("va"))

    def test_url_title_extraction(self):
        slug = extract_title_from_url("https://example.com/deep-space-exploration")
        self.assertIn("deep space", slug.lower())

    def test_tts_voice_demo(self):
        self.assertTrue(hasattr(TTSEngine, "generate_voice_demo"))

    def test_pipeline_attributes(self):
        pipeline = VideoPipeline()
        self.assertIsNotNone(pipeline.script_gen)
        self.assertIsNotNone(pipeline.audio_mixer)
        self.assertIsNotNone(pipeline.subtitle_eng)
        self.assertIsNotNone(pipeline.video_eng)
        self.assertIsNotNone(pipeline.visual_eng)
        self.assertTrue(hasattr(pipeline, "reroll_visuals_for_video"))

    def test_audio_effects_dsp_config(self):
        self.assertIn("studio_warmth", AUDIO_EFFECTS)
        self.assertIn("deep_trailer", AUDIO_EFFECTS)
        self.assertIn("radio_broadcast", AUDIO_EFFECTS)
        self.assertIn("vintage_tape", AUDIO_EFFECTS)
        self.assertEqual(DEFAULT_AUDIO_EFFECT, "studio_warmth")

        tts = TTSEngine(effect_key="deep_trailer")
        self.assertEqual(tts.effect_key, "deep_trailer")
        self.assertIn("aecho", tts.dsp_filter)

    def test_youtube_chapters_generation(self):
        sg = ScriptGenerator()
        scenes = [
            {"scene_num": 1, "text": "Qora tuynuk nima?", "duration": 5.0},
            {"scene_num": 2, "text": "U qanday hosil bo'ladi?", "duration": 6.0},
            {"scene_num": 3, "text": "Bizga obuna bo'ling!", "duration": 4.0}
        ]
        seo = sg.generate_viral_seo_package("Qora tuynuklar", lang="uz", scenes=scenes)
        self.assertIn("youtube_chapters", seo)
        chapters = seo["youtube_chapters"]
        self.assertIn("00:00 - Kirish", chapters)
        self.assertIn("00:05 - ", chapters)
        self.assertIn("00:11 - Xulosa", chapters)

    def test_extract_story_snippet_method(self):
        self.assertTrue(hasattr(VideoPipeline, "extract_story_snippet"))

    def test_ken_burns_camera_motions(self):
        self.assertIn("ken_burns_in", CAMERA_MOTIONS)
        self.assertIn("ken_burns_pan", CAMERA_MOTIONS)
        self.assertEqual(CAMERA_MOTIONS["ken_burns_in"]["mode"], "zoom_in")
        self.assertEqual(CAMERA_MOTIONS["ken_burns_pan"]["mode"], "pan_horiz")

    def test_outro_chime_sfx(self):
        mixer = AudioMixer()
        self.assertTrue(mixer.default_chime.exists())
        self.assertTrue(hasattr(AudioMixer, "_generate_outro_chime"))

    def test_subtitle_header_badge(self):
        se = SubtitleEngine()
        test_ass = str(TEMP_DIR / "test_badge.ass")
        scenes = [{"scene_num": 1, "text": "Test badge", "start_time": 0.0, "end_time": 3.0, "words": []}]
        se.generate_ass(scenes, test_ass, topic_badge="Koinot Sirlari")
        self.assertTrue(os.path.exists(test_ass))
        with open(test_ass, "r", encoding="utf-8") as f:
            content = f.read()
            # Top header banner to'liq olib tashlangan bo'lishi shart (Zero-Banner standarti)
            self.assertNotIn("HeaderBadge", content)
            self.assertNotIn("【", content)
            self.assertIn("Karaoke", content)
        try: os.remove(test_ass)
        except Exception: pass

    def test_multi_platform_seo(self):
        sg = ScriptGenerator()
        seo = sg.generate_viral_seo_package("Biznes va Boylik", lang="uz")
        self.assertIn("tiktok_caption", seo)
        self.assertIn("instagram_caption", seo)
        self.assertIn("Biznes va Boylik", seo["tiktok_caption"])
        self.assertIn("#reels", seo["instagram_caption"])

    def test_cinematic_35mm_filter(self):
        self.assertIn("cinematic_35mm", VISUAL_FILTERS)
        filt = VISUAL_FILTERS["cinematic_35mm"]["filter"]
        self.assertIn("vignette", filt)
        self.assertIn("noise", filt)

    def test_change_video_speed_method(self):
        self.assertTrue(hasattr(VideoPipeline, "change_video_speed"))

    def test_series_plan_generator(self):
        plan = ScriptGenerator.generate_series_plan("Qora tuynuklar", lang="uz")
        self.assertEqual(len(plan), 3)
        self.assertIn("1-Qism", plan[0]["title"])
        self.assertIn("2-Qism", plan[1]["title"])
        self.assertIn("3-Qism", plan[2]["title"])

    def test_engagement_question_in_seo(self):
        sg = ScriptGenerator()
        seo = sg.generate_viral_seo_package("Sun'iy intellekt", lang="uz")
        self.assertIn("engagement_question", seo)
        self.assertIn("Sun'iy intellekt", seo["engagement_question"])

    def test_job_cache_persistence_and_pruning(self):
        from bot import save_job_cache_item, job_cache
        save_job_cache_item("test_job_999", {"topic": "Test"})
        self.assertIn("test_job_999", job_cache)
        job_cache.pop("test_job_999", None)

    def test_audio_mixer_mix_with_vocals_path(self):
        mixer = AudioMixer()
        # Synthesize a 1s sample voice
        test_v1 = str(TEMP_DIR / "test_v1.wav")
        mixer._synthesize_track("lofi_vibes", test_v1, duration=1.0)

        out_master = str(TEMP_DIR / "test_out_master.wav")
        out_vocals = str(TEMP_DIR / "test_out_vocals.wav")

        mixer.mix([test_v1], out_master, genre="lofi_vibes", output_vocals_path=out_vocals)
        self.assertTrue(os.path.exists(out_master))
        self.assertTrue(os.path.exists(out_vocals))
        self.assertGreater(os.path.getsize(out_vocals), 1000)

        for p in [test_v1, out_master, out_vocals]:
            try: os.remove(p)
            except Exception: pass

    def test_cleanup_old_temp_files_includes_user_uploads(self):
        # Create a test old file in USER_UPLOADS_DIR
        test_up = USER_UPLOADS_DIR / "test_stale_upload.tmp"
        test_up.write_text("stale data")
        # Set mtime to 48 hours ago
        past_time = time.time() - (48 * 3600)
        os.utime(test_up, (past_time, past_time))

        VideoPipeline.cleanup_old_temp_files(max_age_hours=1.0)
        self.assertFalse(test_up.exists())

    def test_visual_engine_download_retry_structure(self):
        ve = VisualEngine()
        # Non-existent invalid URL should return False after retries without throwing uncaught exception
        res = ve._download_image("https://invalid-non-existent-domain-12345.xyz/img.jpg", str(TEMP_DIR / "never.jpg"), timeout=1)
        self.assertFalse(res)

    def test_subtitle_engine_missing_words_fallback(self):
        se = SubtitleEngine()
        # Scene without 'words' key should auto-synthesize and generate valid Dialogue lines
        scenes = [{"scene_num": 1, "text": "Koinot va yulduzlar jilosi", "start_time": 0.0, "end_time": 3.0}]
        test_ass = str(TEMP_DIR / "test_missing_words.ass")
        se.generate_ass(scenes, test_ass)
        self.assertTrue(os.path.exists(test_ass))
        with open(test_ass, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Karaoke", content)
            self.assertIn("Koinot", content)
        try: os.remove(test_ass)
        except Exception: pass

    def test_tts_language_failover_logic(self):
        # Verify voice IDs in VOICES config for Russian, English, Uzbek
        self.assertEqual(VOICES["ru_dmitry"]["lang"], "ru")
        self.assertEqual(VOICES["en_christopher"]["lang"], "en")
        self.assertEqual(VOICES["uz_sardor"]["lang"], "uz")

    def test_quick_topic_registration_safe_byte_size(self):
        from bot import register_quick_topic, QUICK_TOPICS
        long_cyrillic = "Кўп қаватли коинот сирлари ҳақида жуда узун ва батафсил мақола sarlavhasi " * 3
        qid = register_quick_topic(long_cyrillic)
        cb_data = f"qgen:{qid}"
        # Telegram strict limit is 64 bytes
        self.assertLessEqual(len(cb_data.encode("utf-8")), 64)
        self.assertEqual(QUICK_TOPICS[qid], long_cyrillic)

    def test_parse_custom_user_script_long_sentence_split(self):
        sg = ScriptGenerator()
        long_text = (
            "Dunyodagi eng katta va chuqur sir bu inson tafakkurining cheksiz imkoniyatlaridir. "
            "Har bir buyuk kashfiyot aynan oddiy savollarga javob izlashdan boshlangan va insoniyat tarixini butunlay o'zgartirib yuborgan. "
            "Bugun ham siz o'z oldingizga katta maqsadlar qo'yib barchasini amalga oshirishingiz mumkin!"
        )
        scenes = sg.parse_custom_user_script(long_text)
        self.assertGreaterEqual(len(scenes), 2)
        for sc in scenes:
            self.assertLessEqual(len(sc["text"]), 240)

    def test_subtitle_engine_curly_brace_sanitization(self):
        se = SubtitleEngine()
        scenes = [{
            "scene_num": 1,
            "text": "Dasturlash {Python} siri \\ test",
            "start_time": 0.0,
            "end_time": 3.0,
            "words": [
                {"word": "{Python}", "start": 0.1, "end": 1.2},
                {"word": "siri\\", "start": 1.3, "end": 2.8}
            ]
        }]
        test_ass = str(TEMP_DIR / "test_brace.ass")
        se.generate_ass(scenes, test_ass, topic_badge="Badge {Test}")
        self.assertTrue(os.path.exists(test_ass))
        with open(test_ass, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("(Python)", content)
            self.assertIn("siri/", content)
            self.assertNotIn("HeaderBadge", content)
        try: os.remove(test_ass)
        except Exception: pass

    def test_uzbek_number_to_words_and_ordinals(self):
        self.assertEqual(uzbek_number_to_words(0), "nol")
        self.assertEqual(uzbek_number_to_words(5), "besh")
        self.assertEqual(uzbek_number_to_words(16), "o'n olti")
        self.assertEqual(uzbek_number_to_words(99), "to'qson to'qqiz")
        self.assertEqual(uzbek_number_to_words(100), "bir yuz")
        self.assertEqual(uzbek_number_to_words(2026), "ikki ming yigirma olti")
        self.assertEqual(to_uzbek_ordinal("ikki ming yigirma olti"), "ikki ming yigirma oltinchi")
        self.assertEqual(to_uzbek_ordinal("bir"), "birinchi")
        self.assertEqual(to_uzbek_ordinal("yigirma"), "yigirmanchi")

    def test_phonetic_uzbek_normalization(self):
        text1 = "2026-yilda insoniyat AI va ChatGPT orqali 99% ishlarni bajaradi."
        norm1 = phonetic_uzbek_normalize(text1)
        self.assertIn("ikki ming yigirma oltinchi yilda", norm1)
        self.assertIn("ey-ay", norm1)
        self.assertIn("Chat-Ji-Pi-Ti", norm1)
        self.assertIn("to'qson to'qqiz foiz", norm1)

        text2 = "Buning narxi $100 yoki 5-10 dollar atrofida."
        norm2 = phonetic_uzbek_normalize(text2)
        self.assertIn("bir yuz dollar", norm2)
        self.assertIn("besh dan o'n gacha dollar", norm2)

        text3 = "U 1-o'rinda turadi va 3 ta usul bor."
        norm3 = phonetic_uzbek_normalize(text3)
        self.assertIn("birinchi o'rinda", norm3)
        self.assertIn("uch ta usul", norm3)

        text4 = "2-qism: YouTube va TikTok orqali 4K formatda ko'ring."
        norm4 = phonetic_uzbek_normalize(text4)
        self.assertIn("ikkinchi qism", norm4)
        self.assertIn("Yutyub", norm4)
        self.assertIn("Tik-Tok", norm4)
        self.assertIn("to'rt ka", norm4)

    def test_voice_cadence_modes(self):
        self.assertEqual(DEFAULT_VOICE_MODE, "vodiy_viral")
        expected_modes = [
            "vodiy_viral", "toshkent_adabiy", "samarqand_epik",
            "xorazm_shirin", "voha_baxshi", "city_podcast",
            "koinot_mystic", "trailer_power"
        ]
        for m in expected_modes:
            self.assertIn(m, VOICE_MODES)
            self.assertIn("cadence", VOICE_MODES[m])
            self.assertIn("rate", VOICE_MODES[m])
            self.assertIn("pitch", VOICE_MODES[m])

        tts_vodiy = TTSEngine(voice_key="uz_sardor", mode_key="vodiy_viral")
        self.assertEqual(tts_vodiy.cadence, "viral_hook")

        tts_sam = TTSEngine(voice_key="uz_sardor", mode_key="samarqand_epik")
        self.assertEqual(tts_sam.cadence, "epic_story")

        tts_xorazm = TTSEngine(voice_key="uz_sardor", mode_key="xorazm_shirin")
        self.assertEqual(tts_xorazm.cadence, "xorazm_flow")

        tts_voha = TTSEngine(voice_key="uz_sardor", mode_key="voha_baxshi")
        self.assertEqual(tts_voha.cadence, "voha_epic")

    def test_phonetic_uzbek_advanced(self):
        text1 = "Bahosi 2.5 million so'm va uning maydoni 50 m² atrofida."
        norm1 = phonetic_uzbek_normalize(text1)
        self.assertIn("ikki butun o'ndan besh million so'm", norm1)
        self.assertIn("ellik kvadrat metr", norm1)

        text2 = "Poyezd soat 14:30 da yo'lga chiqadi va tezligi 120 km/soat."
        norm2 = phonetic_uzbek_normalize(text2)
        self.assertIn("o'n to'rt o'ttiz", norm2)
        self.assertIn("bir yuz yigirma kilometr soatiga", norm2)

        text3 = "AQSH va BMT vakillari 2026-yilda uchrashadi."
        norm3 = phonetic_uzbek_normalize(text3)
        self.assertIn("Amerika Qo'shma Shtatlari", norm3)
        self.assertIn("Be-Em-Te", norm3)

    def test_cadence_dialect_procedural_generation(self):
        sg = ScriptGenerator()
        sc_sam = sg._generate_procedural("Koinot", "uz", "top_facts", 3, voice_mode="samarqand_epik")
        self.assertIn("Qadim zamonlardan", sc_sam[0]["text"])

        sc_vodiy = sg._generate_procedural("Koinot", "uz", "top_facts", 3, voice_mode="vodiy_viral")
        self.assertIn("Qani, do'stlar", sc_vodiy[0]["text"])

        sc_city = sg._generate_procedural("Koinot", "uz", "top_facts", 3, voice_mode="city_podcast")
        self.assertIn("Keling", sc_city[0]["text"])

    def test_smart_dsp_synergy(self):
        tts_sam = TTSEngine(voice_key="uz_sardor", mode_key="samarqand_epik")
        self.assertEqual(tts_sam.effect_key, "deep_trailer")

        tts_vodiy = TTSEngine(voice_key="uz_sardor", mode_key="vodiy_viral")
        self.assertEqual(tts_vodiy.effect_key, "studio_warmth")

        tts_city = TTSEngine(voice_key="uz_sardor", mode_key="city_podcast")
        self.assertEqual(tts_city.effect_key, "studio_warmth")

        tts_mystic = TTSEngine(voice_key="uz_sardor", mode_key="koinot_mystic")
        self.assertEqual(tts_mystic.effect_key, "deep_trailer")

    def test_phonetic_breath_pauses_and_sanitation(self):
        text = "Biz buni bilamiz chunki u muhim lekin amal qilmaymiz???"
        norm = phonetic_uzbek_normalize(text)
        self.assertIn("bilamiz, chunki", norm)
        self.assertIn("muhim, lekin", norm)
        self.assertTrue(norm.endswith("?"))
        self.assertNotIn("???", norm)

    def test_cadence_podcast_dialogue(self):
        sg = ScriptGenerator()
        sc_sam = sg._generate_procedural("Tarix", "uz", "podcast_dialogue", 3, voice_mode="samarqand_epik")
        self.assertIn("azaliy hikmat", sc_sam[0]["text"])

        sc_vodiy = sg._generate_procedural("Tarix", "uz", "podcast_dialogue", 3, voice_mode="vodiy_viral")
        self.assertIn("Qarang", sc_vodiy[0]["text"])

        sc_city = sg._generate_procedural("Tarix", "uz", "podcast_dialogue", 3, voice_mode="city_podcast")
        self.assertIn("Do'stlar", sc_city[0]["text"])

        sc_xorazm = sg._generate_procedural("Tarix", "uz", "podcast_dialogue", 3, voice_mode="xorazm_shirin")
        self.assertIn("Og'ajon", sc_xorazm[0]["text"])

        sc_voha = sg._generate_procedural("Tarix", "uz", "podcast_dialogue", 3, voice_mode="voha_baxshi")
        self.assertIn("mardona", sc_voha[0]["text"])

    def test_parse_custom_user_script_and_text_modes(self):
        sg = ScriptGenerator()
        custom_text = (
            "1. Sun'iy intellekt kelajakni qanday o'zgartirmoqda?\n"
            "2. Har kuni yangi texnologiyalar paydo bo'lmoqda.\n"
            "3. O'zbekiston yoshlari ham bu sohada yetakchi bo'ladi!"
        )
        scenes = sg.parse_custom_user_script(custom_text, topic="AI Kelajak")
        self.assertEqual(len(scenes), 3)
        self.assertIn("Sun'iy intellekt", scenes[0]["text"])
        self.assertIn("yetakchi", scenes[2]["text"])

    def test_main_keyboard_create_text_button(self):
        kb = get_main_keyboard()
        buttons = [btn.text for row in kb.inline_keyboard for btn in row]
        self.assertTrue(any("Matn / Ssenariy Yuborish" in b for b in buttons))
        callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        self.assertIn("menu_create_text", callbacks)

if __name__ == "__main__":
    unittest.main()
