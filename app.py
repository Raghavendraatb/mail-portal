import os
from flask import Flask, render_template
from flask_cors import CORS
from imap_client import fetch_emails

app = Flask(__name__)
CORS(app)

@app.route("/")
def inbox():
    emails = fetch_emails()
    return render_template("inbox.html", emails=emails)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)