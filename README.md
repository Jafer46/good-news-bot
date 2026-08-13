# Good News Ethiopia Bot

Reads new posts from a source Telegram channel (e.g. Tikvah), uses Gemini to
filter for genuinely good news, translates + summarizes to English, and
posts to your own channel with a link back to the original — on a free
GitHub Actions schedule.

## How it works

`main.py` runs every 30 minutes via GitHub Actions:
1. `telegram_reader.py` fetches any posts newer than the last one it saw
2. `ai_processor.py` sends each post to Gemini, which returns whether it's
   good news, a confidence score, a full English translation, and a summary
3. If it's good news above the confidence threshold, `poster.py` posts it to
   your channel with an expandable "full translation" section and a link to
   the original
4. `state.py` remembers the last post id so nothing gets posted twice

## One-time setup

### 1. Get Telegram API credentials (for reading the source channel)
Go to https://my.telegram.org → API Development Tools → create an app.
You'll get an `api_id` and `api_hash`.

### 2. Generate a session string
On your own machine:
```bash
pip install telethon
python generate_session.py
```
Enter your phone number and the login code Telegram sends you. Copy the
printed session string — you'll need it below. Keep it private, it's
equivalent to being logged into your Telegram account.

### 3. Create your bot (for posting to your channel)
Message [@BotFather](https://t.me/BotFather) on Telegram, run `/newbot`,
and save the token it gives you.

### 4. Create your destination channel
Create "Good News Ethiopia" as a Telegram channel, then add your new bot as
an **admin** (needs permission to post messages).

To get the channel's numeric ID: forward any message from the channel to
[@userinfobot](https://t.me/userinfobot), or just use `@YourChannelUsername`
directly if the channel is public.

### 5. Get a free Gemini API key
Go to https://aistudio.google.com/apikey and create a key. No credit card
needed for the free tier.

### 6. Add secrets to your GitHub repo
Push this project to a new GitHub repo, then go to
**Settings → Secrets and variables → Actions → New repository secret** and
add each of these:

| Secret name | Value |
|---|---|
| `TELEGRAM_API_ID` | from step 1 |
| `TELEGRAM_API_HASH` | from step 1 |
| `TELEGRAM_SESSION` | from step 2 |
| `SOURCE_CHANNEL` | e.g. `tikvahethiopia` (no @) |
| `TELEGRAM_BOT_TOKEN` | from step 3 |
| `DEST_CHANNEL_ID` | from step 4 |
| `GEMINI_API_KEY` | from step 5 |

### 7. (Recommended) Set a sane starting point
`state.json` starts at `"last_seen_id": 0`, which means the very first run
will try to process the entire channel history. To start fresh from "now"
instead, open the source channel in Telegram, find the most recent post's
id (visible in its link, e.g. `t.me/tikvahethiopia/4821` → id `4821`), and
set `state.json` to that number before your first push.

### 8. Turn it on
GitHub Actions will run automatically every 30 minutes once this is pushed
with the workflow file in `.github/workflows/run.yml`. You can also trigger
it manually from the **Actions** tab → "Good News Ethiopia Bot" →
**Run workflow**.

## Tuning

- **Posting frequency**: edit the cron schedule in
  `.github/workflows/run.yml` (`*/30 * * * *` = every 30 min).
- **Strictness**: raise or lower `GOOD_NEWS_CONFIDENCE_THRESHOLD` in the
  workflow file (0–1). Higher = fewer, more confidently-"good" posts.
- **Multiple sources**: currently reads one `SOURCE_CHANNEL`. To add more,
  loop over a list of channel usernames in `telegram_reader.py` and track
  a separate `last_seen_id` per channel in `state.json`.

## A note on the "authenticity" requirement

Automated classification can misjudge edge cases (satire, rumors dressed as
news, etc). Consider running this for a couple of weeks in "review mode"
first: point `DEST_CHANNEL_ID` at a private channel only you can see, check
that the classifications look right, and only then switch it to point at
your real public channel.
