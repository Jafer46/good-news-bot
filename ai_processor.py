import os
import json
import re
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

MODEL_NAME = "gemini-2.5-flash"

PROMPT_TEMPLATE = """You are a careful news editor. You will be given a social
media post, likely in Amharic (it may contain some English too).

Do all of the following and respond with ONLY a raw JSON object, no markdown
fences, no extra commentary:

1. "is_good_news": true only if the post reports a genuinely positive,
   uplifting, constructive news event (e.g. achievement, recovery, progress,
   aid, discovery, community good deed). False for neutral news, bad news,
   ads, opinion pieces, rumors, or anything you are not confident is a real
   reported news event.
2. "confidence": your confidence in the is_good_news judgment, from 0 to 1.
3. "translation_full": a complete, faithful English translation of the post.
   Do not add information that isn't in the original.
4. "summary": a neutral 2-3 sentence English summary of the post.
5. "reason": one short sentence explaining your is_good_news judgment.

If the post is not primarily a news report at all (e.g. it's an ad, a poll,
a meme with no real content), set is_good_news to false and confidence to 1.

POST:
---
{post_text}
---
"""


def process_post(post_text: str) -> dict | None:
    """
    Returns a dict with is_good_news, confidence, translation_full, summary,
    reason -- or None if the model call failed / response was unparseable.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = PROMPT_TEMPLATE.format(post_text=post_text)

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        raw = response.text.strip()
    except Exception as e:
        print(f"Gemini call failed: {e}")
        return None

    # Defensive cleanup in case the model wraps output in ```json fences
    raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Could not parse Gemini response as JSON: {e}\nRaw: {raw}")
        return None

    required_keys = {"is_good_news", "confidence", "translation_full", "summary", "reason"}
    if not required_keys.issubset(data.keys()):
        print(f"Gemini response missing required keys: {data}")
        return None

    return data
