import os
import time

from telegram_reader import fetch_new_posts
from ai_processor import process_post
from poster import post_good_news
from state import load_last_seen_id, save_last_seen_id

CONFIDENCE_THRESHOLD = float(os.environ.get("GOOD_NEWS_CONFIDENCE_THRESHOLD", "0.75"))


def main():
    last_seen_id = load_last_seen_id()
    print(f"Last seen post id: {last_seen_id}")

    posts = fetch_new_posts(last_seen_id)
    print(f"Fetched {len(posts)} new post(s)")

    if not posts:
        return

    highest_id_seen = last_seen_id

    for post in posts:
        highest_id_seen = max(highest_id_seen, post["id"])

        result = process_post(post["text"])
        if result is None:
            print(f"[{post['id']}] Skipped — AI processing failed")
            continue

        is_good = result["is_good_news"]
        confidence = result["confidence"]
        print(f"[{post['id']}] is_good_news={is_good} confidence={confidence} reason={result['reason']}")

        if is_good and confidence >= CONFIDENCE_THRESHOLD:
            posted = post_good_news(
                summary=result["summary"],
                translation_full=result["translation_full"],
                source_link=post["link"],
            )
            print(f"[{post['id']}] Posted: {posted}")
        else:
            print(f"[{post['id']}] Not posted (not good news, or low confidence)")

        # Be gentle with the free-tier rate limits
        time.sleep(2)

    # Save progress even if some posts failed to process, so we don't
    # reprocess them forever — they were still "seen".
    save_last_seen_id(highest_id_seen)
    print(f"Updated last seen post id to: {highest_id_seen}")


if __name__ == "__main__":
    main()
