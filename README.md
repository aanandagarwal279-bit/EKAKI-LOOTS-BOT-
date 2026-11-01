# EKAKI LOOTS Bot

A conservative starter bot for forwarding eligible deal posts from approved Telegram channels to your EKAKI LOOTS channel.

## Important Telegram requirements
- The bot must be added as an administrator to every source channel so Telegram delivers `channel_post` updates.
- The bot must be an administrator in the destination channel with permission to post.
- This bot does **not** scrape arbitrary channels, bypass private-channel access, or read channels where it lacks permission.
- Start a private chat with the bot before expecting owner messages.

## What this starter currently does
- Accepts channel posts only from configured numeric source IDs.
- Requires at least one HTTP(S) link and a rupee price in the text.
- Skips a small list of common URL shorteners.
- Deduplicates using title + URL fingerprint.
- Posts a simple Hinglish-friendly deal card.
- Schedules a Sunday 20:00 Asia/Kolkata report.

## Limitations — do not treat this as production-ready
- Link checking is syntactic only; it does not verify retailer stock, real price, discount, product identity, or affiliate attribution.
- Commission is not automatically fetched. Weekly commission remains ₹0 unless a trusted integration/manual record is added.
- Report counters are lifetime totals in this starter, not a true weekly breakdown yet.
- No guaranteed 24/7 uptime: deployment host, quotas, sleep policies and Telegram availability matter.
- No affiliate links are generated. Add only links from an approved affiliate program and follow its age, KYC, disclosure and guardian requirements.
- Do not publish copied images/content unless source permissions allow it.

## Setup
1. Create a private copy of `.env.example` named `.env` on your host. Never commit `.env`.
2. Fill in bot token, source channel IDs, destination channel ID and owner chat ID.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

For local testing, use a secure secret manager or environment variables instead of committing secrets.

## Safe rollout
Start with one source channel you control, test with a non-public destination, and verify every post manually before enabling public posting.
