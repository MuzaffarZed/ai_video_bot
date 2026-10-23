"""
MuzaffarZed AI Video Bot - Telegram Bot Interfeysi (aiogram 3.x)
To'liq avtomatlashtirilgan, interaktiv inline panelli va jonli progressga ega bot.
Muallif: MuzaffarZed
"""
import os
import sys
import asyncio
import logging

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

from config import TELEGRAM_BOT_TOKEN, VOICES, DEFAULT_VOICE, WATERMARK_TEXT
from pipeline import VideoPipeline

# Logging sozlash
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Foydalanuvchilar sozlamalari (xotirada)
user_settings = {}
active_tasks = set()
pipeline = VideoPipeline()

def get_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎙 Ovozni tanlash", callback_data="menu_voice"),
        InlineKeyboardButton(text="💡 Tezkor Mavzular", callback_data="menu_topics")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="menu_about")
    )
    return builder.as_markup()

def get_voice_keyboard(current_voice: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, v in VOICES.items():
        check = "✅ " if key == current_voice else ""
        builder.row(InlineKeyboardButton(text=f"{check}{v['name']}", callback_data=f"set_voice:{key}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu_main"))
    return builder.as_markup()

def get_topics_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    topics = [
        "🌌 Koinotning eng sirli hodisalari",
        "🧠 Muvaffaqiyatli insonlarning 3 ta siri",
        "🤖 Sun'iy intellekt kelajakni qanday o'zgartiradi",
        "💰 Moliyaviy erkinlikka erishish qoidasi",
        "⚡ Qadimgi dunyoning yechilmagan jumboqlari"
    ]
    for top in topics:
        builder.row(InlineKeyboardButton(text=top, callback_data=f"quick_gen:{top}"))
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu_main"))
    return builder.as_markup()

dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_settings:
        user_settings[user_id] = {"voice": DEFAULT_VOICE}

    welcome_text = (
        f"👋 Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        f"🎬 <b>MuzaffarZed AI Video Bot</b>ga xush kelibsiz!\n\n"
        f"Men bir necha soniyada istalgan mavzuda professional <b>Full HD (9:16) Reels/Shorts</b> video tayyorlab bera olaman:\n"
        f"• 🧠 <i>Viral ssenariy va kadrlar taqsimoti</i>\n"
        f"• 🎙 <i>Neyron audio (O'zbek, Rus, Ingliz)</i>\n"
        f"• 🎨 <i>AI chizgan 8K vertikal tasvirlar</i>\n"
        f"• 🎵 <i>Fon musiqasi (Audio Ducking)</i>\n"
        f"• 📝 <i>Zamonaviy Karaoke subtitrlar</i>\n\n"
        f"🚀 <b>Video yaratish uchun shunchaki mavzuni yozib yuboring</b> yoki quyidagi tugmalardan birini tanlang:\n\n"
        f"<i>{WATERMARK_TEXT}</i>"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "menu_main")
async def cb_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎬 Bosh menyu: Video mavzusini yozib yuboring yoki quyidagilardan tanlang:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(F.data == "menu_voice")
async def cb_voice_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    cur_voice = user_settings.get(user_id, {}).get("voice", DEFAULT_VOICE)
    await callback.message.edit_text(
        "🎙 <b>Videongiz qaysi tilda va kimning ovozida bo'lishini tanlang:</b>",
        reply_markup=get_voice_keyboard(cur_voice),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("set_voice:"))
async def cb_set_voice(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    voice_key = callback.data.split(":")[1]
    if user_id not in user_settings:
        user_settings[user_id] = {}
    user_settings[user_id]["voice"] = voice_key
    voice_name = VOICES[voice_key]["name"]
    await callback.answer(f"Tanlandi: {voice_name}")
    await callback.message.edit_text(
        f"✅ Ovoz o'zgartirildi: <b>{voice_name}</b>\n\nEndi videongiz mavzusini yozing:",
        reply_markup=get_voice_keyboard(voice_key),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "menu_topics")
async def cb_topics_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "💡 <b>Tezkor tayyor mavzulardan birini tanlang:</b>",
        reply_markup=get_topics_keyboard(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "menu_about")
async def cb_about_menu(callback: types.CallbackQuery):
    about_text = (
        "💎 <b>MuzaffarZed Professional AI Video Generator</b>\n\n"
        "Ushbu tizim eng ilg'or sun'iy intellekt texnologiyalarini o'zida birlashtirgan:\n"
        "• <b>Video Dvigateli:</b> FFmpeg 60 FPS + Ken Burns Dynamics\n"
        "• <b>Ovoz:</b> Microsoft Neural Edge-TTS High-Definition\n"
        "• <b>Vizual:</b> Pollinations AI Diffusion 8K Photorealistic\n"
        "• <b>Subtitr:</b> Dynamic Millisecond Karaoke Text Render\n\n"
        f"<i>{WATERMARK_TEXT}</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu_main"))
    await callback.message.edit_text(about_text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("quick_gen:"))
async def cb_quick_generate(callback: types.CallbackQuery):
    topic = callback.data[len("quick_gen:"):]
    await callback.answer(f"Tanlandi: {topic[:25]}...")
    await handle_video_creation(callback.message, topic, callback.from_user.id)

@dp.message(F.text)
async def msg_handle_text(message: types.Message):
    topic = message.text.strip()
    if topic.startswith("/"):
        return
    await handle_video_creation(message, topic, message.from_user.id)

async def handle_video_creation(message: types.Message, topic: str, user_id: int):
    if user_id in active_tasks:
        await message.answer("⚠️ Hozirda sizning videongiz tayyorlanmoqda, iltimos u yakunlanishini kuting!")
        return

    active_tasks.add(user_id)
    cur_voice = user_settings.get(user_id, {}).get("voice", DEFAULT_VOICE)

    status_msg = await message.answer(
        f"🎬 <b>Yangi video yaratish boshlandi!</b>\n\n"
        f"📌 <b>Mavzu:</b> <i>{topic}</i>\n"
        f"🎙 <b>Ovoz:</b> <i>{VOICES[cur_voice]['name']}</i>\n\n"
        f"⏳ <i>Iltimos kuting, montaj jarayoni ketmoqda...</i>",
        parse_mode="HTML"
    )

    last_update_text = ""

    async def progress_notifier(step: int, total: int, status_text: str):
        nonlocal last_update_text
        if status_text != last_update_text:
            last_update_text = status_text
            try:
                progress_bar = "▓" * (step * 2) + "░" * ((total - step) * 2)
                await status_msg.edit_text(
                    f"🎬 <b>Video yaratilmoqda... [{step}/{total}]</b>\n\n"
                    f"📌 <b>Mavzu:</b> <i>{topic}</i>\n"
                    f"<code>[{progress_bar}]</code>\n\n"
                    f"<b>{status_text}</b>\n\n"
                    f"<i>{WATERMARK_TEXT}</i>",
                    parse_mode="HTML"
                )
            except Exception:
                pass

    try:
        result = await pipeline.create_video(
            topic=topic,
            voice_key=cur_voice,
            progress_callback=progress_notifier
        )

        video_path = result["video_path"]
        dur = result["duration"]

        await status_msg.edit_text(
            f"✨ <b>Video muvaffaqiyatli tayyorlandi!</b>\n\n"
            f"🚀 Telegramga yuklanmoqda...",
            parse_mode="HTML"
        )

        # Videoni yuborish
        video_file = FSInputFile(video_path)
        caption_text = (
            f"🎬 <b>{topic}</b>\n\n"
            f"⏱ Davomiyligi: {dur:.1f} soniya\n"
            f"📱 Formati: 1080x1920 (9:16 Full HD)\n\n"
            f"<i>{WATERMARK_TEXT}</i>"
        )

        await message.answer_video(
            video=video_file,
            caption=caption_text,
            width=1080,
            height=1920,
            supports_streaming=True,
            parse_mode="HTML"
        )
        await status_msg.delete()

    except Exception as e:
        logger.exception("Video yaratishda xato")
        await status_msg.edit_text(
            f"❌ <b>Xatolik yuz berdi:</b>\n<code>{str(e)[:200]}</code>\n\nIltimos boshqa mavzuni sinab ko'ring.",
            parse_mode="HTML"
        )
    finally:
        active_tasks.discard(user_id)

async def main():
    token = TELEGRAM_BOT_TOKEN
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("=" * 65)
        print("⚠️ DIQQAT: TELEGRAM_BOT_TOKEN sozlanmagan!")
        print("1. @BotFather dan yangi bot yarating va token oling.")
        print("2. Tokenni .env fayliga yoki config.py ga joylang:")
        print("   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIjk...")
        print("=" * 65)
        sys.exit(1)

    bot = Bot(token=token)
    print("=" * 65)
    print("🤖 MUZAFFARZED AI VIDEO TELEGRAM BOT ISHGA TUSHDI!")
    print("Polling rejimi faollashtirildi...")
    print("=" * 65)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
