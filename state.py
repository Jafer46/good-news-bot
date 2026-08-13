import json
import os

STATE_PATH = os.path.join(os.path.dirname(__file__), "state.json")


def load_last_seen_id() -> int:
    if not os.path.exists(STATE_PATH):
        return 0
    with open(STATE_PATH, "r") as f:
        return json.load(f).get("last_seen_id", 0)


def save_last_seen_id(post_id: int) -> None:
    with open(STATE_PATH, "w") as f:
        json.dump({"last_seen_id": post_id}, f, indent=2)
