"""Management of Telegram bot messages and interactions."""

import os
import threading
from typing import List

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from .gemini_service import extract_products
from .search_engine import search_stalls

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parse incoming message and reply with matching stalls."""
    if not update.message:
        return
    products = extract_products(update.message.text)
    stalls = search_stalls(products)
    if not stalls:
        await update.message.reply_text("\u0645\u062d\u0635\u0648\u0644\u06cc \u06cc\u0627\u0641\u062a \u0646\u0634\u062f.")
        return
    lines = [f"{stall['name']}: {', '.join(stall['products'])}" for stall in stalls]
    await update.message.reply_text("\n".join(lines))


def start_bot() -> None:
    """Start the Telegram bot in a background thread."""
    if not BOT_TOKEN:
        print("BOT_TOKEN is not set.")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    thread = threading.Thread(target=application.run_polling, kwargs={"poll_interval": 3}, daemon=True)
    thread.start()
