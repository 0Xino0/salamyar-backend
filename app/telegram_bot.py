"""Management of Telegram bot messages and interactions."""

import os
import threading
from typing import List
import asyncio  # <--- ۱. این خط باید اضافه شود

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from .gemini_service import extract_products
from .search_engine import search_vendor_overlap


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parse incoming message and reply with matching stalls and Gemini raw output."""
    if not update.message:
        return
    products, raw_output = extract_products(update.message.text)
    if not products:
        await update.message.reply_text("محصولی یافت نشد.")
        return
    # Call Basalam per product, find overlapping vendors
    # Run the blocking search in a thread to avoid blocking the async handler
    result = await asyncio.to_thread(search_vendor_overlap, products)
    vendors = result.get("vendors", [])
    items = result.get("matches", [])
    if not vendors:
        await update.message.reply_text("هیچ غرفه‌ای حداقل دو محصول درخواستی شما را ندارد.")
        return
    # Prepare per-vendor, per-query grouped messages with product URLs
    # Build lookup of items by (vendor_id, query_term)
    from collections import defaultdict
    grouped: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for it in items:
        key = (it.get("vendor_id"), it.get("query_term") or "")
        grouped[key].append(it)

    BASE_URL = "https://basalam.com"

    for vendor in vendors:
        vendor_id = vendor["vendor_id"]
        vendor_name = vendor.get("vendor_name") or ""
        # Start message with vendor heading
        lines: list[str] = [f"{vendor_name} (ID: {vendor_id})", ""]
        # For each original query in order, list products of this vendor that match that query
        for term in products:
            vendor_query_items = grouped.get((vendor_id, term), [])
            if not vendor_query_items:
                continue
            lines.append(f"{term}:")
            lines.append("")
            for it in vendor_query_items:
                product_name = it.get("product_name") or ""
                product_id = it.get("product_id")
                # Construct product address per requested pattern
                product_address = f"{BASE_URL}/p/{product_id}"
                lines.append(product_name)
                lines.append(product_address)
                lines.append("")
        # Send one message per vendor
        message_text = "\n".join(lines).strip()
        if message_text:
            await update.message.reply_text(message_text)


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