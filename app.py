import os
from flask import Flask, render_template
from flask_cors import CORS
from imap_client import fetch_emails
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

@app.route("/")
def inbox():
    logger.info("Inbox endpoint hit")

    emails = fetch_emails()
    logger.info(f"Fetched {len(emails)} emails")

    return render_template("inbox.html", emails=emails)

@app.route("/")
def inbox():
    emails = fetch_emails()
    return render_template("inbox.html", emails=emails)

@app.route("/health")
def health():
    return {"status": "UP"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)