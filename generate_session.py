"""
Run this ONCE on your own machine (not in GitHub Actions).

It logs you into Telegram interactively (asks for your phone number and the
login code Telegram sends you), then prints a session string. Paste that
string into your GitHub repo secret TELEGRAM_SESSION so the bot can read
messages headlessly in Actions without logging in again.

Usage:
    pip install telethon
    python generate_session.py
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(input("Enter your API ID (from my.telegram.org): ").strip())
api_hash = input("Enter your API Hash (from my.telegram.org): ").strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    session_string = client.session.save()
    print("\n\nSave this as the TELEGRAM_SESSION secret in GitHub:\n")
    print(session_string)
    print("\nKeep it secret — anyone with this string can log in as you.\n")
