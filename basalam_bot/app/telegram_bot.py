"""Management of Telegram bot messages and interactions."""

import os
import threading
from typing import List
import asyncio  # <--- ۱. این خط باید اضافه شود

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from .gemini_service import extract_products
from .search_engine import search_vendor_overlap, _fetch_search_results_for_product


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parse incoming message and reply with matching stalls and Gemini raw output."""
    if not update.message:
        return
    products, raw_output = extract_products(update.message.text)
    # Format and send the Gemini JSON output first
    formatted_output += "\n\nExtracted Products:\n"
    formatted_output += f"{products}\n"
    formatted_output += "═══════════════\n"
    await update.message.reply_text(formatted_output)
    
    # Call Basalam per product, find overlapping vendors, and present minimal JSON
    # Run the blocking search in a thread to avoid blocking the async handler
    matches = await asyncio.to_thread(search_vendor_overlap, products)
    if not matches:
        await update.message.reply_text("محصول مشترکی بین غرفه‌ها یافت نشد.")
        return
    # Respond as JSON with required fields
    import json
    await update.message.reply_text(
        json.dumps(matches, ensure_ascii=False, indent=2)
    )

    # Debugging: Send raw output of Basalam search for each product with status code and error handling
    for term in products:
        try:
            payload = await asyncio.to_thread(_fetch_search_results_for_product, term)
            if not payload:
                await update.message.reply_text(f"Raw output for product '{term}': EMPTY RESPONSE")
            else:
                await update.message.reply_text(
                    f"Raw output for product '{term}':\n" + json.dumps(payload, ensure_ascii=False, indent=2)
                )
        except Exception as e:
            await update.message.reply_text(f"Error fetching data for product '{term}': {str(e)}")


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