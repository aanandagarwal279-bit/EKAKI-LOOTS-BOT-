import asyncio
import logging
import os
from datetime import time
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, ContextTypes, MessageHandler, CommandHandler, filters
)

from bot.deals import extract_deal, is_duplicate, save_deal, weekly_stats
from bot.publisher import publish_deal

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("ekaki-loots")

TOKEN = os.getenv("BOT_TOKEN", "").strip()
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL_ID", "").strip()
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID", "").strip()
SOURCE_IDS = {
    x.strip() for x in os.getenv("SOURCE_CHANNEL_IDS", "").split(",") if x.strip()
}
TZ = ZoneInfo("Asia/Kolkata")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "EKAKI LOOTS bot is running. Use /status to check configuration."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot status: running\\n"
        f"Approved sources configured: {len(SOURCE_IDS)}\\n"
        f"Target channel configured: {'yes' if TARGET_CHANNEL else 'no'}"
    )


async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post = update.channel_post
    if not post or not post.chat:
        return

    source_id = str(post.chat.id)
    if source_id not in SOURCE_IDS:
        return

    text = post.text or post.caption or ""
    deal = extract_deal(text)
    if not deal:
        log.info("Skipped source post: no usable text/link/price")
        return

    if is_duplicate(deal["fingerprint"]):
        log.info("Skipped duplicate deal")
        return

    if not TARGET_CHANNEL:
        log.error("TARGET_CHANNEL_ID is not configured")
        return

    try:
        await publish_deal(context.bot, TARGET_CHANNEL, deal)
        save_deal(deal, source_id, post.message_id)
        log.info("Published deal from source %s", source_id)
    except Exception:
        log.exception("Could not publish deal")


async def weekly_report(context: ContextTypes.DEFAULT_TYPE):
    if not OWNER_CHAT_ID:
        log.warning("OWNER_CHAT_ID missing; weekly report not sent")
        return
    stats = weekly_stats()
    message = (
        "📊 EKAKI LOOTS — Weekly Report\\n\\n"
        f"Collected & published: {stats['published']}\\n"
        f"Skipped duplicates: {stats['duplicates']}\\n"
        f"Tracked commission: ₹{stats['commission']:.2f}\\n\\n"
        "Note: commission is shown only when manually recorded/verified. "
        "Clicks and estimated earnings are not treated as confirmed income."
    )
    await context.bot.send_message(chat_id=int(OWNER_CHAT_ID), text=message)


def main():
    if not TOKEN:
        raise SystemExit("BOT_TOKEN is missing. Set it in your environment.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST, handle_channel_post))

    # Every Sunday at 20:00 India time. Requires python-telegram-bot job-queue extra.
    if app.job_queue:
        app.job_queue.run_daily(
            weekly_report,
            time=time(hour=20, minute=0, tzinfo=TZ),
            days=(6,),
            name="weekly-report",
        )
    else:
        log.warning("JobQueue unavailable; install python-telegram-bot[job-queue]")

    log.info("Starting EKAKI LOOTS bot")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
