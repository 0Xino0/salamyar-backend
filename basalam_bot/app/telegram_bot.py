"""Management of Telegram bot messages and interactions."""

import os
import threading
from typing import List
import asyncio  # <--- ۱. این خط باید اضافه شود

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from .gemini_service import extract_products
from .search_engine import search_stalls


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parse incoming message and reply with matching stalls."""
    if not update.message:
        return
    products = extract_products(update.message.text)
    stalls = search_stalls(products)
    if not stalls:
        await update.message.reply_text("محصولی یافت نشد.")
        return
    lines = [f"{stall['name']}: {', '.join(stall['products'])}" for stall in stalls]
    await update.message.reply_text("\n".join(lines))


def start_bot() -> None:
    """Start the Telegram bot in a background thread."""
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    if not BOT_TOKEN:
        print("BOT_TOKEN is not set.")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ۲. یک تابع کمکی برای مدیریت event loop در thread جدید تعریف می‌کنیم
    def run_polling_in_new_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.run_polling(poll_interval=3))

    # ۳. این thread جدید را با تابع کمکی اجرا می‌کنیم
    thread = threading.Thread(target=run_polling_in_new_loop, daemon=True)
    thread.start()