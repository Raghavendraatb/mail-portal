import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from imap_client import fetch_emails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates")
CORS(app)


@app.route("/", methods=["GET", "HEAD"])
def inbox():
    if request.method == "HEAD":
        return "", 200

    try:
        emails = fetch_emails()
        logger.info(f"Rendered {len(emails)} emails")
        return render_template(
            "inbox.html",
            emails=emails,
            refreshed=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        )
    except Exception as e:
        logger.exception("Failed to load inbox")
        return render_template(
            "inbox.html",
            emails=[],
            error="Could not fetch emails",
            refreshed=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        ), 500


@app.route("/health")
def health():
    return jsonify(status="UP"), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)