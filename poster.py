import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
DEST_CHANNEL_ID = os.environ["DEST_CHANNEL_ID"]

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Telegram hard-caps sendMessage text at 4096 characters (including HTML tags).
# Leave headroom for the summary, link, and markup around the blockquote.
TELEGRAM_MAX_LEN = 4096
SAFETY_MARGIN = 300


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_message(summary: str, translation_full: str, source_link: str) -> str:
    summary_html = _escape_html(summary)
    full_html = _escape_html(translation_full)

    budget = TELEGRAM_MAX_LEN - SAFETY_MARGIN - len(summary_html) - len(source_link)
    if len(full_html) > budget:
        full_html = full_html[: max(budget, 0)].rstrip() + "… (truncated — see original)"

    return (
        "🟢 <b>Good News Ethiopia</b>\n\n"
        f"{summary_html}\n\n"
        f"<blockquote expandable>{full_html}</blockquote>\n\n"
        f'🔗 <a href="{source_link}">Original post</a>'
    )


def post_good_news(summary: str, translation_full: str, source_link: str) -> bool:
    text = build_message(summary, translation_full, source_link)

    resp = requests.post(
        API_URL,
        json={
            "chat_id": DEST_CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=30,
    )

    if not resp.ok:
        print(f"Failed to post to Telegram: {resp.status_code} {resp.text}")
        return False

    return True