import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession


def fetch_new_posts(last_seen_id: int, limit: int = 50):
    """
    Returns a list of new text posts from SOURCE_CHANNEL with id > last_seen_id,
    oldest first. Each item is a dict: {id, text, link}
    """
    api_id = int(os.environ["TELEGRAM_API_ID"])
    api_hash = os.environ["TELEGRAM_API_HASH"]
    session_string = os.environ["TELEGRAM_SESSION"]
    source_channel = os.environ["SOURCE_CHANNEL"]

    posts = []

    with TelegramClient(StringSession(session_string), api_id, api_hash) as client:
        channel = client.get_entity(source_channel)

        # min_id excludes that id and returns everything newer than it
        messages = client.iter_messages(channel, min_id=last_seen_id, reverse=True)

        for msg in messages:
            if not msg.text:
                continue  # skip photo-only / non-text posts
            posts.append(
                {
                    "id": msg.id,
                    "text": msg.text,
                    "link": f"https://t.me/{source_channel}/{msg.id}",
                }
            )
            if len(posts) >= limit:
                break

    return posts
