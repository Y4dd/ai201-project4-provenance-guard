import uuid
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from audit_log import append_entry, get_entries, find_entry
from scoring import generate_label, score_confidence
from signals import groq_ai_score, stylometric_score

app = Flask(__name__)

# A genuine writer submitting their own work makes a handful of submissions
# in a sitting, not dozens; a script flooding the system to probe or abuse
# the Groq-backed pipeline looks very different. 10/minute comfortably covers
# real usage bursts (e.g. resubmitting after edits) while still capping the
# damage a flood script can do; 100/day bounds sustained abuse across a
# session without blocking a prolific creator's normal daily use.
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute;100 per day")
def submit():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    creator_id = data.get("creator_id")

    if not text or not creator_id:
        return jsonify({"error": "text and creator_id are required"}), 400

    content_id = str(uuid.uuid4())
    llm_score = groq_ai_score(text)
    stylometric = stylometric_score(text)
    confidence, attribution = score_confidence(llm_score, stylometric)
    label = generate_label(confidence, attribution)

    entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_score,
        "stylometric_score": stylometric,
        "status": "classified",
    }
    append_entry(entry)

    return jsonify(
        {
            "content_id": content_id,
            "attribution": attribution,
            "confidence": confidence,
            "label": label,
        }
    )


@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json(silent=True) or {}
    content_id = data.get("content_id")
    creator_reasoning = data.get("creator_reasoning")

    if not content_id or not creator_reasoning:
        return jsonify({"error": "content_id and creator_reasoning are required"}), 400

    original = find_entry(content_id)
    if original is None:
        return jsonify({"error": "no submission found for that content_id"}), 404

    entry = {
        "content_id": content_id,
        "creator_id": original["creator_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": original["attribution"],
        "confidence": original["confidence"],
        "llm_score": original["llm_score"],
        "stylometric_score": original["stylometric_score"],
        "status": "under_review",
        "appeal_reasoning": creator_reasoning,
    }
    append_entry(entry)

    return jsonify(
        {
            "content_id": content_id,
            "status": "under_review",
            "message": "Appeal received and logged for review.",
        }
    )


@app.route("/log", methods=["GET"])
def log():
    return jsonify({"entries": get_entries()})


if __name__ == "__main__":
    app.run(debug=True)
