import json
import os

LOG_PATH = os.path.join(os.path.dirname(__file__), "audit_log.json")


def _read_all():
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r") as f:
        return json.load(f)


def append_entry(entry):
    entries = _read_all()
    entries.append(entry)
    with open(LOG_PATH, "w") as f:
        json.dump(entries, f, indent=2)


def get_entries():
    return _read_all()


def find_entry(content_id):
    for entry in reversed(_read_all()):
        if entry["content_id"] == content_id:
            return entry
    return None
