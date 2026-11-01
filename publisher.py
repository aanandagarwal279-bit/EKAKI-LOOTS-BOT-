from telegram.constants import ParseMode


async def publish_deal(bot, target_channel, deal):
    # Keep source text compact and clearly identify the link.
    text = (
        f"🔥 <b>{escape(deal['title'])}</b>\n\n"
        f"💰 Price mentioned: ₹{escape(deal['price'])}\n"
        f"🔗 <a href=\"{escape(deal['url'])}\">View deal</a>\n\n"
        "ℹ️ Price/availability can change. Please verify on the retailer page."
    )
    await bot.send_message(
        chat_id=target_channel,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=False,
    )


def escape(value):
    from html import escape as html_escape
    return html_escape(str(value), quote=True)
