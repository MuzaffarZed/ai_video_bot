"""
MuzaffarZed AI Video Bot - Telegram Bot Interfeysi (aiogram 3.x - Infinity 5.0 Ultra Studio)
Ovozli xabarlardan video yasash (Voice to Reels), 1-Click format konvertatsiya, Real-Time AI Art, MP3 va Statistika.
Muallif: MuzaffarZed
"""
import os
import sys
import time
import json
import asyncio
import logging
import html
import subprocess
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import (
    BASE_DIR,
    TEMP_DIR,
    TELEGRAM_BOT_TOKEN,
    USER_UPLOADS_DIR,
    VOICES,
    DEFAULT_VOICE,
    VOICE_MODES,
    DEFAULT_VOICE_MODE,
    VIDEO_STYLES,
    DEFAULT_VIDEO_STYLE,
    DURATIONS,
    DEFAULT_DURATION,
    FORMATS,
    DEFAULT_FORMAT,
    SUBTITLE_THEMES,
    DEFAULT_SUBTITLE_THEME,
    MUSIC_GENRES,
    DEFAULT_MUSIC_GENRE,
    WATERMARK_TEXT,
    BRAND_NAME
)
from pipeline import VideoPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

USER_DB_FILE = BASE_DIR / "user_db.json"
STATS_FILE = BASE_DIR / "bot_stats.json"

def load_json(file_path: Path, default_data: dict) -> dict:
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data
    return default_data

def save_json(file_path: Path, data: dict):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Fayl saqlashda xato ({file_path}): {e}")

user_settings = load_json(USER_DB_FILE, {})
bot_stats = load_json(STATS_FILE, {"total_videos": 0, "total_users": 0, "users_list": []})
user_active_requests = set()
user_pending_photos = {}
job_cache = {}
pipeline = VideoPipeline()
render_lock = asyncio.Lock()

def record_user(user_id: int):
    uid = str(user_id)
    if uid not in bot_stats["users_list"]:
        bot_stats["users_list"].append(uid)
        bot_stats["total_users"] = len(bot_stats["users_list"])
        save_json(STATS_FILE, bot_stats)

def record_video_generation():
    bot_stats["total_videos"] = bot_stats.get("total_videos", 0) + 1
    save_json(STATS_FILE, bot_stats)

def get_user_pref(user_id: int, key: str, default: str) -> str:
    uid = str(user_id)
    if uid in user_settings and key in user_settings[uid]:
        return user_settings[uid][key]
    return default

def set_user_pref(user_id: int, key: str, value: str):
    uid = str(user_id)
    if uid not in user_settings:
        user_settings[uid] = {}
    user_settings[uid][key] = value
    save_json(USER_DB_FILE, user_settings)

# ==================== KLAAVIATURALAR ====================

def get_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎙 Ovoz", callback_data="menu_voice"),
        InlineKeyboardButton(text="⚡ Tezlik & Rejim", callback_data="menu_modes")
    )
    builder.row(
        InlineKeyboardButton(text="🎛 Uslub", callback_data="menu_styles"),
        InlineKeyboardButton(text="🎨 Subtitr", callback_data="menu_themes")
    )
    builder.row(
        InlineKeyboardButton(text="📱 Format (9:16/16:9)", callback_data="menu_formats"),
        InlineKeyboardButton(text="⏱ Davomiylik", callback_data="menu_duration")
    )
    builder.row(
        InlineKeyboardButton(text="🎵 Fon Musiqasi", callback_data="menu_music"),
        InlineKeyboardButton(text="💡 Tezkor Mavzular", callback_data="menu_topics")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="menu_about"),
        InlineKeyboardButton(text="📊 Statistika", callback_data="menu_stats")
    )
    return builder.as_markup()

def get_voice_keyboard(current: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, v in VOICES.items():
        check = "✅ " if key == current else ""
        builder.row(InlineKeyboardButton(text=f"{check}{v['name']}", callback_data=f"set_voice:{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    return builder.as_markup()

def get_modes_keyboard(current: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, m in VOICE_MODES.items():
        check = "✅ " if key == current else ""
        builder.row(InlineKeyboardButton(text=f"{check}{m['name']}", callback_data=f"set_mode:{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    return builder.as_markup()

def get_styles_keyboard(current: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, s in VIDEO_STYLES.items():
        check = "✅ " if key == current else ""
        builder.row(InlineKeyboardButton(text=f"{check}{s['name']}", callback_data=f"set_style:{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    return builder.as_markup()

def get_formats_keyboard(current: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, f in FORMATS.items():
        check = "✅ " if key == current else ""
        builder.row(InlineKeyboardButton(text=f"{check}{f['name']}", callback_data=f"set_format:{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    return builder.as_markup()

def get_duration_keyboard(current: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, d in DURATIONS.items():
        check = "✅ " if key == current else ""
        builder.row(InlineKeyboardButton(text=f"{check}{d['name']}", callback_data=f"set_duration:{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    return builder.as_markup()

def get_themes_keyboard(current: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, t in SUBTITLE_THEMES.items():
        check = "✅ " if key == current else ""
        builder.row(InlineKeyboardButton(text=f"{check}{t['name']}", callback_data=f"set_theme:{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    return builder.as_markup()

def get_music_keyboard(current: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, m in MUSIC_GENRES.items():
        check = "✅ " if key == current else ""
        builder.row(InlineKeyboardButton(text=f"{check}{m}", callback_data=f"set_music:{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    return builder.as_markup()

def get_topics_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    topics = [
        "🌌 Koinotning eng sirli hodisalari",
        "🧠 Muvaffaqiyatli insonlarning 3 ta siri",
        "🤖 Sun'iy intellekt kelajakni qanday o'zgartiradi",
        "💰 Moliyaviy erkinlikka erishish qoidasi",
        "⚡ Qadimgi dunyoning yechilmagan jumboqlari",
        "🏃 Sog'lom hayot va intizom kuchi"
    ]
    for top in topics:
        builder.row(InlineKeyboardButton(text=top, callback_data=f"quick_gen:{top}"))
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    return builder.as_markup()

def get_post_video_keyboard(task_id: str, current_fmt: str = "9:16") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎙 Audio MP3 yuklab olish", callback_data=f"dl_mp3:{task_id}"),
        InlineKeyboardButton(text="📝 Ssenariy matni", callback_data=f"view_script:{task_id}")
    )
    if current_fmt == "9:16":
        builder.row(InlineKeyboardButton(text="🖥 YouTube (16:9) ga o'girish", callback_data=f"re_render:{task_id}:16:9"))
    else:
        builder.row(InlineKeyboardButton(text="📱 Reels (9:16) ga o'girish", callback_data=f"re_render:{task_id}:9:16"))

    builder.row(
        InlineKeyboardButton(text="💡 Yangi mavzular", callback_data="menu_topics"),
        InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="menu_main")
    )
    return builder.as_markup()

dp = Dispatcher()

# ==================== BUYRUQLAR (COMMANDS) ====================

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    record_user(user_id)

    cur_voice = get_user_pref(user_id, "voice", DEFAULT_VOICE)
    cur_style = get_user_pref(user_id, "style", DEFAULT_VIDEO_STYLE)
    cur_fmt = get_user_pref(user_id, "format", DEFAULT_FORMAT)

    v_name = VOICES.get(cur_voice, VOICES[DEFAULT_VOICE])["name"]
    s_name = VIDEO_STYLES.get(cur_style, VIDEO_STYLES[DEFAULT_VIDEO_STYLE])["name"]
    f_name = FORMATS.get(cur_fmt, FORMATS[DEFAULT_FORMAT])["name"]

    welcome_text = (
        f"👋 Assalomu alaykum, <b>{html.escape(message.from_user.full_name)}</b>!\n\n"
        f"🎬 <b>{BRAND_NAME} (Infinity 5.0 Ultra)</b>ga xush kelibsiz!\n\n"
        f"Men bir zumda jahon darajasidagi video montaj qilib beraman:\n"
        f"• 🎙 <b>Ovoz:</b> {v_name}\n"
        f"• 🎛 <b>Uslub:</b> {s_name}\n"
        f"• 📱 <b>Format:</b> {f_name}\n"
        f"• 🎨 <b>AI Vizual:</b> <i>Real-Time Pollinations AI + 4K Unsplash</i>\n"
        f"• 🎚 <b>Studio DSP:</b> <i>EBU R128 + Sidechain Audio Ducking</i>\n"
        f"• 🎥 <b>Dinamika:</b> <i>Dynamic Zoom & Pan + Oltin progress chizig'i</i>\n\n"
        f"🚀 <b>Qanday ishlatiladi:</b>\n"
        f"1. ✍️ <b>Matn yozing:</b> Mavzuni yozing va video oling;\n"
        f"2. 📸 <b>Rasm yuboring:</b> O'z suratingizdan Reels yasang;\n"
        f"3. 🎙 <b>Ovozli xabar yuboring:</b> O'z ovozingizdan avtomatik video montaj oling!\n\n"
        f"<i>{WATERMARK_TEXT}</i>"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        f"📖 <b>{BRAND_NAME} - Qo'llanma:</b>\n\n"
        "1. <b>Matndan video:</b> Mavzuni yozing (masalan: <i>Qora tuynuklar siri</i>) — AI ssenariy tuzadi, chizadi va montaj qiladi.\n"
        "2. <b>Rasmdan video:</b> Surat yuboring — bot uni 1-kadr sifatida kinoviy vinyetka bilan montaj qiladi.\n"
        "3. <b>Ovozdan video:</b> Telegramda ovozli xabar yozib yuboring — bot ovozingizni tozalab, 4K video ulab beradi!\n\n"
        "Buyruqlar:\n"
        "/start - Bosh menyu\n"
        "/settings - Sozlamalar paneli\n"
        "/stats - Bot statistikasi\n"
        "/help - Qo'llanma\n\n"
        f"<i>{WATERMARK_TEXT}</i>"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    await message.answer("⚙️ <b>Sozlamalar paneli:</b> Quyidagi menyulardan birini tanlang:", reply_markup=get_main_keyboard(), parse_mode="HTML")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    total_u = bot_stats.get("total_users", len(bot_stats.get("users_list", [])))
    total_v = bot_stats.get("total_videos", 0)
    stats_text = (
        f"📊 <b>{BRAND_NAME} - Tizim Statistikasi:</b>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {total_u} ta\n"
        f"🎬 <b>Yaratilgan videolar:</b> {total_v} ta\n"
        f"☁️ <b>Bulut Serveri:</b> 24/7 Faol (GitHub Actions)\n"
        f"💎 <b>Dvigatel:</b> Infinity 5.0 Ultra Studio\n\n"
        f"<i>{WATERMARK_TEXT}</i>"
    )
    await message.answer(stats_text, parse_mode="HTML")

@dp.callback_query(F.data == "menu_stats")
async def cb_stats(callback: types.CallbackQuery):
    total_u = bot_stats.get("total_users", len(bot_stats.get("users_list", [])))
    total_v = bot_stats.get("total_videos", 0)
    stats_text = (
        f"📊 <b>{BRAND_NAME} - Tizim Statistikasi:</b>\n\n"
        f"👥 <b>Foydalanuvchilar:</b> {total_u} ta\n"
        f"🎬 <b>Yaratilgan videolar:</b> {total_v} ta\n"
        f"☁️ <b>Server:</b> 24/7 Bulutda Faol\n\n"
        f"<i>{WATERMARK_TEXT}</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    await callback.message.edit_text(stats_text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "menu_main")
async def cb_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎬 <b>Bosh menyu:</b> Video mavzusini yozib yuboring yoki quyidagilardan birini sozlang:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

# --- Format menyusi ---
@dp.callback_query(F.data == "menu_formats")
async def cb_formats_menu(callback: types.CallbackQuery):
    cur = get_user_pref(callback.from_user.id, "format", DEFAULT_FORMAT)
    await callback.message.edit_text("📱 <b>Video formatini tanlang:</b>", reply_markup=get_formats_keyboard(cur), parse_mode="HTML")

@dp.callback_query(F.data.startswith("set_format:"))
async def cb_set_format(callback: types.CallbackQuery):
    key = callback.data.split(":")[1]
    set_user_pref(callback.from_user.id, "format", key)
    f_name = FORMATS[key]["name"]
    await callback.answer(f"Format: {f_name}")
    await callback.message.edit_text(f"✅ Format o'rnatildi: <b>{f_name}</b>", reply_markup=get_formats_keyboard(key), parse_mode="HTML")

# --- Davomiylik menyusi ---
@dp.callback_query(F.data == "menu_duration")
async def cb_duration_menu(callback: types.CallbackQuery):
    cur = get_user_pref(callback.from_user.id, "duration", DEFAULT_DURATION)
    await callback.message.edit_text("⏱ <b>Video davomiyligini tanlang:</b>", reply_markup=get_duration_keyboard(cur), parse_mode="HTML")

@dp.callback_query(F.data.startswith("set_duration:"))
async def cb_set_duration(callback: types.CallbackQuery):
    key = callback.data.split(":")[1]
    set_user_pref(callback.from_user.id, "duration", key)
    d_name = DURATIONS[key]["name"]
    await callback.answer(f"Davomiylik: {d_name}")
    await callback.message.edit_text(f"✅ Davomiylik o'rnatildi: <b>{d_name}</b>", reply_markup=get_duration_keyboard(key), parse_mode="HTML")

# --- Ovoz menyusi ---
@dp.callback_query(F.data == "menu_voice")
async def cb_voice_menu(callback: types.CallbackQuery):
    cur = get_user_pref(callback.from_user.id, "voice", DEFAULT_VOICE)
    await callback.message.edit_text("🎙 <b>Videongiz qaysi tilda va kimning ovozida bo'lsin:</b>", reply_markup=get_voice_keyboard(cur), parse_mode="HTML")

@dp.callback_query(F.data.startswith("set_voice:"))
async def cb_set_voice(callback: types.CallbackQuery):
    key = callback.data.split(":")[1]
    set_user_pref(callback.from_user.id, "voice", key)
    v_name = VOICES[key]["name"]
    await callback.answer(f"Ovoz: {v_name}")
    await callback.message.edit_text(f"✅ Ovoz o'rnatildi: <b>{v_name}</b>", reply_markup=get_voice_keyboard(key), parse_mode="HTML")

# --- Tezlik menyusi ---
@dp.callback_query(F.data == "menu_modes")
async def cb_modes_menu(callback: types.CallbackQuery):
    cur = get_user_pref(callback.from_user.id, "mode", DEFAULT_VOICE_MODE)
    await callback.message.edit_text("⚡ <b>Ovoz tezligi va tonalitesini tanlang:</b>", reply_markup=get_modes_keyboard(cur), parse_mode="HTML")

@dp.callback_query(F.data.startswith("set_mode:"))
async def cb_set_mode(callback: types.CallbackQuery):
    key = callback.data.split(":")[1]
    set_user_pref(callback.from_user.id, "mode", key)
    m_name = VOICE_MODES[key]["name"]
    await callback.answer(f"Rejim: {m_name}")
    await callback.message.edit_text(f"✅ Rejim o'rnatildi: <b>{m_name}</b>", reply_markup=get_modes_keyboard(key), parse_mode="HTML")

# --- Uslub menyusi ---
@dp.callback_query(F.data == "menu_styles")
async def cb_styles_menu(callback: types.CallbackQuery):
    cur = get_user_pref(callback.from_user.id, "style", DEFAULT_VIDEO_STYLE)
    await callback.message.edit_text("🎛 <b>Video ssenariy uslubini tanlang:</b>", reply_markup=get_styles_keyboard(cur), parse_mode="HTML")

@dp.callback_query(F.data.startswith("set_style:"))
async def cb_set_style(callback: types.CallbackQuery):
    key = callback.data.split(":")[1]
    set_user_pref(callback.from_user.id, "style", key)
    s_name = VIDEO_STYLES[key]["name"]
    await callback.answer(f"Uslub: {s_name}")
    await callback.message.edit_text(f"✅ Video uslubi o'rnatildi: <b>{s_name}</b>", reply_markup=get_styles_keyboard(key), parse_mode="HTML")

# --- Subtitr menyusi ---
@dp.callback_query(F.data == "menu_themes")
async def cb_themes_menu(callback: types.CallbackQuery):
    cur = get_user_pref(callback.from_user.id, "theme", DEFAULT_SUBTITLE_THEME)
    await callback.message.edit_text("🎨 <b>Subtitr neon rang sxemasini tanlang:</b>", reply_markup=get_themes_keyboard(cur), parse_mode="HTML")

@dp.callback_query(F.data.startswith("set_theme:"))
async def cb_set_theme(callback: types.CallbackQuery):
    key = callback.data.split(":")[1]
    set_user_pref(callback.from_user.id, "theme", key)
    t_name = SUBTITLE_THEMES[key]["name"]
    await callback.answer(f"Rang: {t_name}")
    await callback.message.edit_text(f"✅ Subtitr dizayni o'rnatildi: <b>{t_name}</b>", reply_markup=get_themes_keyboard(key), parse_mode="HTML")

# --- Musiqa menyusi ---
@dp.callback_query(F.data == "menu_music")
async def cb_music_menu(callback: types.CallbackQuery):
    cur = get_user_pref(callback.from_user.id, "music", DEFAULT_MUSIC_GENRE)
    await callback.message.edit_text("🎵 <b>Fon musiqasi janrini tanlang:</b>", reply_markup=get_music_keyboard(cur), parse_mode="HTML")

@dp.callback_query(F.data.startswith("set_music:"))
async def cb_set_music(callback: types.CallbackQuery):
    key = callback.data.split(":")[1]
    set_user_pref(callback.from_user.id, "music", key)
    m_name = MUSIC_GENRES[key]
    await callback.answer(f"Musiqa: {m_name}")
    await callback.message.edit_text(f"✅ Fon musiqasi: <b>{m_name}</b>", reply_markup=get_music_keyboard(key), parse_mode="HTML")

# --- Mavzular menyusi ---
@dp.callback_query(F.data == "menu_topics")
async def cb_topics_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("💡 <b>Tezkor tayyor mavzulardan birini tanlang:</b>", reply_markup=get_topics_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "menu_about")
async def cb_about_menu(callback: types.CallbackQuery):
    about_text = (
        f"💎 <b>{BRAND_NAME} (Infinity 5.0 Ultra Studio)</b>\n\n"
        "• <b>Real-Time AI:</b> Pollinations AI 8K + 4K Unsplash + Oflayn grafika\n"
        "• <b>Formatlar:</b> 9:16 Vertikal, 16:9 Gorizontal, 1:1 Kvadrat\n"
        "• <b>Ovoz:</b> Microsoft Neural + Studio Broadcast DSP (EBU R128, Warmth)\n"
        "• <b>Video Dvigateli:</b> Dynamic Zoom & Pan + Oltin progress chizig'i + Kinoviy vinyetka\n"
        "• <b>Subtitr:</b> Alex Hormozi Karaoke 2.0 (4 xil rang, 118% pop kattalashuv)\n"
        "• <b>Musiqa:</b> 4 ta janr + Sidechain Audio Ducking + Whoosh SFX\n"
        "• <b>Qo'shimcha:</b> Foydalanuvchi ovozi va rasmini qabul qilish, 1-Click format o'zgartirish\n\n"
        f"<i>{WATERMARK_TEXT}</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Bosh menyu", callback_data="menu_main"))
    await callback.message.edit_text(about_text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("quick_gen:"))
async def cb_quick_generate(callback: types.CallbackQuery):
    topic = callback.data[len("quick_gen:"):]
    await callback.answer(f"Tanlandi: {topic[:25]}...")
    await handle_video_creation(callback.message, topic, callback.from_user.id)

# --- MP3 podkast yuklab olish ---
@dp.callback_query(F.data.startswith("dl_mp3:"))
async def cb_dl_mp3(callback: types.CallbackQuery):
    task_id = callback.data.split(":")[1]
    job_info = job_cache.get(task_id)
    if job_info and os.path.exists(job_info.get("mp3_path", "")):
        await callback.answer("Audio yuklanmoqda...")
        audio_file = FSInputFile(job_info["mp3_path"])
        await callback.message.answer_audio(
            audio=audio_file,
            title=job_info.get("topic", "Audio Podkast")[:50],
            performer="MuzaffarZed AI Studio",
            caption=f"🎙 <b>{html.escape(job_info.get('topic', ''))}</b>\n\n<i>{WATERMARK_TEXT}</i>",
            parse_mode="HTML"
        )
    else:
        await callback.answer("⚠️ Audio fayl topilmadi.", show_alert=True)

# --- Ssenariy matnini ko'rish ---
@dp.callback_query(F.data.startswith("view_script:"))
async def cb_view_script(callback: types.CallbackQuery):
    task_id = callback.data.split(":")[1]
    job_info = job_cache.get(task_id)
    if job_info and job_info.get("script_text"):
        await callback.answer("Ssenariy matni ochilmoqda...")
        await callback.message.answer(
            f"📝 <b>Video ssenariysi ({html.escape(job_info.get('topic', ''))}):</b>\n\n"
            f"<code>{html.escape(job_info['script_text'])}</code>\n\n"
            f"<i>{WATERMARK_TEXT}</i>",
            parse_mode="HTML"
        )
    else:
        await callback.answer("⚠️ Ssenariy topilmadi.", show_alert=True)

# --- 1-Click Format Re-render ---
@dp.callback_query(F.data.startswith("re_render:"))
async def cb_re_render(callback: types.CallbackQuery):
    parts = callback.data.split(":")
    task_id = parts[1]
    new_fmt = f"{parts[2]}:{parts[3]}"
    job_info = job_cache.get(task_id)
    if not job_info:
        await callback.answer("⚠️ Ma'lumotlar eskirgan, yangi mavzu yozing.", show_alert=True)
        return

    topic = job_info["topic"]
    set_user_pref(callback.from_user.id, "format", new_fmt)
    await callback.answer(f"Format: {new_fmt} ga o'tkazilmoqda...")
    await handle_video_creation(callback.message, topic, callback.from_user.id)

# ==================== OVOZLI XABAR (VOICE NOTE) HANDLERI ====================

@dp.message(F.voice | F.audio)
async def msg_handle_voice(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    record_user(user_id)

    if user_id in user_active_requests:
        await message.answer("⚠️ Hozirda sizning videongiz tayyorlanmoqda, iltimos u yakunlanishini kuting!")
        return

    user_active_requests.add(user_id)
    status_msg = await message.answer("🎙 <b>Ovozli xabaringiz qabul qilindi!</b>\n\n🎧 Studiya DSP orqali tozalash va 4K video montaj boshlanmoqda...", parse_mode="HTML")

    task_id = f"voice_{int(time.time())}"
    raw_voice = TEMP_DIR / f"{task_id}_raw.ogg"
    clean_wav = TEMP_DIR / f"{task_id}_clean.wav"
    out_video = OUTPUT_DIR / f"{task_id}_final.mp4"

    try:
        voice_obj = message.voice or message.audio
        file_info = await bot.get_file(voice_obj.file_id)
        await bot.download_file(file_info.file_path, destination=raw_voice)

        # OGG ni WAV ga o'girish va EBU R128 studiya DSP qo'llash
        dsp_cmd = [
            "ffmpeg", "-nostdin", "-y",
            "-i", str(raw_voice),
            "-af", "highpass=f=80,equalizer=f=220:t=q:w=1.2:g=2.8,equalizer=f=3600:t=q:w=1.0:g=3.2,compand=attacks=0.02:decays=0.1:points=-80/-80|-25/-15|-10/-5|0/0:soft-knee=6,loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:a", "pcm_s16le",
            "-ar", "44100",
            str(clean_wav)
        ]
        await asyncio.to_thread(subprocess.run, dsp_cmd, capture_output=True, check=True)

        dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(clean_wav)]
        res = await asyncio.to_thread(subprocess.run, dur_cmd, capture_output=True, text=True, check=True)
        total_dur = float(res.stdout.strip())

        cur_format = get_user_pref(user_id, "format", DEFAULT_FORMAT)
        fmt_info = FORMATS.get(cur_format, FORMATS[DEFAULT_FORMAT])

        # Fon musiqasi mikslari
        master_audio = str(TEMP_DIR / f"{task_id}_master.wav")
        await asyncio.to_thread(pipeline.audio_mixer.mix, [str(clean_wav)], master_audio, genre="ambient_chill")

        # 4K rasm generatsiyasi
        img_path = str(TEMP_DIR / f"{task_id}_img.jpg")
        await asyncio.to_thread(pipeline.visual_eng.get_scene_visual, "voice podcast storytelling cinematic", img_path)

        clip_path = str(TEMP_DIR / f"{task_id}_clip.mp4")
        await asyncio.to_thread(pipeline.video_eng.render_scene_clip, img_path, total_dur, clip_path, 1, cur_format)

        # Final video
        await asyncio.to_thread(
            pipeline.video_eng.assemble_final_video,
            [clip_path],
            master_audio,
            "",
            str(out_video),
            total_dur,
            "gold",
            cur_format
        )

        record_video_generation()
        video_file = FSInputFile(str(out_video))
        caption_text = (
            f"🎙 <b>Sizning Ovozli Xabaringizdan Video Reels</b>\n\n"
            f"⏱ <b>Davomiyligi:</b> {total_dur:.1f}s | 📱 <b>Format:</b> {fmt_info['name']}\n"
            f"💎 <b>Sifat:</b> Studio DSP Mastering + Dynamic Ambient\n\n"
            f"<i>{WATERMARK_TEXT}</i>"
        )

        await message.answer_video(
            video=video_file,
            caption=caption_text,
            width=fmt_info["width"],
            height=fmt_info["height"],
            supports_streaming=True,
            parse_mode="HTML"
        )
        await status_msg.delete()

    except Exception as e:
        logger.exception("Ovozdan video yasashda xato")
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: <code>{html.escape(str(e)[:250])}</code>", parse_mode="HTML")
    finally:
        user_active_requests.discard(user_id)
        pipeline.cleanup_task_files(task_id)

# ==================== FOYDALANUVCHI RASMI HANDLERI ====================

@dp.message(F.photo)
async def msg_handle_photo(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    record_user(user_id)

    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_ext = os.path.splitext(file_info.file_path)[1] or ".jpg"
    saved_path = USER_UPLOADS_DIR / f"user_{user_id}_{int(time.time())}{file_ext}"

    await bot.download_file(file_info.file_path, destination=saved_path)

    if message.caption and len(message.caption.strip()) >= 3:
        topic = message.caption.strip()
        await handle_video_creation(message, topic, user_id, custom_image_path=str(saved_path))
    else:
        user_pending_photos[user_id] = str(saved_path)
        await message.answer(
            "📸 <b>Ajoyib rasm qabul qilindi!</b>\n\n"
            "Endi ushbu rasm ustiga yaratmoqchi bo'lgan video mavzusi yoki matnini yozib yuboring "
            "(masalan: <i>Muvaffaqiyat kaliti</i>):",
            parse_mode="HTML"
        )

# ==================== MATN HANDLERI ====================

@dp.message(F.text)
async def msg_handle_text(message: types.Message):
    topic = message.text.strip()
    if topic.startswith("/"):
        return

    user_id = message.from_user.id
    record_user(user_id)

    if len(topic) < 3 or topic.lower() in ["salom", "qalesan", "qalaysiz", "hi", "hello"]:
        await message.answer(
            "💡 Iltimos, video yaratish uchun aniqroq mavzu yozing (masalan: <i>Koinot sirlari</i>, <i>Sun'iy intellekt</i> yoki <i>Muvaffaqiyat qoidalari</i>):",
            reply_markup=get_topics_keyboard(),
            parse_mode="HTML"
        )
        return

    custom_img = user_pending_photos.pop(user_id, None)
    await handle_video_creation(message, topic, user_id, custom_image_path=custom_img)

# ==================== ASOSIY VIDEO YARATISH LOGIKASI ====================

async def handle_video_creation(message: types.Message, topic: str, user_id: int, custom_image_path: str = None):
    if user_id in user_active_requests:
        await message.answer("⚠️ Hozirda sizning videongiz tayyorlanmoqda, iltimos u yakunlanishini kuting!")
        return

    user_active_requests.add(user_id)
    cur_voice = get_user_pref(user_id, "voice", DEFAULT_VOICE)
    cur_mode = get_user_pref(user_id, "mode", DEFAULT_VOICE_MODE)
    cur_style = get_user_pref(user_id, "style", DEFAULT_VIDEO_STYLE)
    cur_theme = get_user_pref(user_id, "theme", DEFAULT_SUBTITLE_THEME)
    cur_music = get_user_pref(user_id, "music", DEFAULT_MUSIC_GENRE)
    cur_duration = get_user_pref(user_id, "duration", DEFAULT_DURATION)
    cur_format = get_user_pref(user_id, "format", DEFAULT_FORMAT)

    fmt_info = FORMATS.get(cur_format, FORMATS[DEFAULT_FORMAT])

    status_msg = await message.answer(
        f"🎬 <b>Yangi video yaratish boshlandi!</b>\n\n"
        f"📌 <b>Mavzu:</b> <i>{html.escape(topic)}</i>\n"
        f"🎙 <b>Ovoz:</b> <i>{VOICES[cur_voice]['name']}</i>\n"
        f"📱 <b>Format:</b> <i>{fmt_info['name']}</i>\n"
        f"🎛 <b>Uslub:</b> <i>{VIDEO_STYLES[cur_style]['name']}</i>\n\n"
        f"⏳ <i>Iltimos kuting, montaj navbatiga qo'shilmoqda...</i>",
        parse_mode="HTML"
    )

    last_edit_time = 0.0

    async def progress_notifier(step: int, total: int, status_text: str):
        nonlocal last_edit_time
        now = time.time()
        if (now - last_edit_time < 1.4) and (step < total):
            return

        last_edit_time = now
        try:
            percent = int((step / total) * 100)
            progress_bar = "▓" * (step * 2) + "░" * ((total - step) * 2)
            await status_msg.edit_text(
                f"🎬 <b>Video montaj qilinmoqda... [{percent}%]</b>\n\n"
                f"📌 <b>Mavzu:</b> <i>{html.escape(topic)}</i>\n"
                f"<code>[{progress_bar}]</code>\n\n"
                f"<b>{status_text}</b>\n\n"
                f"<i>{WATERMARK_TEXT}</i>",
                parse_mode="HTML"
            )
        except Exception:
            pass

    try:
        async with render_lock:
            result = await pipeline.create_video(
                topic=topic,
                voice_key=cur_voice,
                voice_mode=cur_mode,
                style_key=cur_style,
                theme_key=cur_theme,
                music_key=cur_music,
                duration_key=cur_duration,
                format_key=cur_format,
                custom_image_path=custom_image_path,
                progress_callback=progress_notifier
            )

        video_path = result["video_path"]
        mp3_path = result.get("mp3_path")
        script_text = result.get("script_text", "")
        dur = result["duration"]
        task_id = result.get("task_id")
        music_genre = result.get("music_genre", "ambient_chill")
        genre_name = MUSIC_GENRES.get(music_genre, music_genre)

        record_video_generation()

        if task_id:
            job_cache[task_id] = {
                "topic": topic,
                "mp3_path": mp3_path,
                "script_text": script_text,
                "format_key": cur_format
            }

        try:
            await status_msg.edit_text(
                "✨ <b>Video muvaffaqiyatli montaj qilindi!</b>\n\n🚀 Telegramga yuklanmoqda...",
                parse_mode="HTML"
            )
        except Exception:
            pass

        video_file = FSInputFile(video_path)
        caption_text = (
            f"🎬 <b>{html.escape(topic)}</b>\n\n"
            f"🎙 <b>Ovoz:</b> {VOICES[cur_voice]['name']} | {VOICE_MODES[cur_mode]['name']}\n"
            f"🎛 <b>Uslub:</b> {VIDEO_STYLES[cur_style]['name']}\n"
            f"🎵 <b>Musiqa:</b> {genre_name} (Sidechain Ducking)\n"
            f"⏱ <b>Davomiyligi:</b> {dur:.1f}s | 📱 <b>Format:</b> {fmt_info['name']}\n"
            f"💎 <b>Sifat:</b> Studio DSP + Alex Hormozi Karaoke 5.0\n\n"
            f"<i>{WATERMARK_TEXT}</i>"
        )

        sent = False
        for attempt in range(3):
            try:
                await message.answer_video(
                    video=video_file,
                    caption=caption_text,
                    width=fmt_info["width"],
                    height=fmt_info["height"],
                    supports_streaming=True,
                    reply_markup=get_post_video_keyboard(task_id, cur_format),
                    parse_mode="HTML"
                )
                sent = True
                break
            except Exception as net_err:
                logger.warning(f"Video yuklash urinishi #{attempt+1} xatosi: {net_err}")
                await asyncio.sleep(2)

        if not sent:
            raise RuntimeError("Telegram serveriga videoni yuborib bo'lmadi.")

        try:
            await status_msg.delete()
        except Exception:
            pass

        if task_id:
            pipeline.cleanup_task_files(task_id)

    except Exception as e:
        logger.exception("Video yaratishda xato")
        err_msg = html.escape(str(e)[:250])
        try:
            await status_msg.edit_text(
                f"❌ <b>Xatolik yuz berdi:</b>\n<code>{err_msg}</code>\n\nIltimos boshqa mavzuni sinab ko'ring.",
                reply_markup=get_main_keyboard(),
                parse_mode="HTML"
            )
        except Exception:
            pass
    finally:
        user_active_requests.discard(user_id)

async def main():
    token = TELEGRAM_BOT_TOKEN
    if not token:
        print("TELEGRAM_BOT_TOKEN topilmadi")
        sys.exit(1)

    bot = Bot(token=token)
    print("=" * 65)
    print("🤖 MUZAFFARZED AI VIDEO BOT (INFINITY 5.0 ULTRA) ISHGA TUSHDI!")
    print("Voice to Reels, Custom Photos, 1-Click Format Conversion faol...")
    print("=" * 65)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
