import imaplib
import email
import os
import logging
from email.header import decode_header

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")


def decode(value):
    if not value:
        return ""
    parts = decode_header(value)
    return "".join(
        str(p[0], p[1] or "utf-8") if isinstance(p[0], bytes) else str(p[0])
        for p in parts
    )


def fetch_emails(limit=50):
    logger.info("Connecting to Gmail IMAP")

    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    mail.select("inbox")

    # ✅ FETCH ALL MAILS
    _, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    logger.info(f"Total emails found: {len(email_ids)}")

    emails = []

    # ✅ Newest first
    for eid in reversed(email_ids[-limit:]):
        _, data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        subject = decode(msg.get("subject"))
        sender = decode(msg.get("from"))
        to_addr = decode(msg.get("to"))     
        date = msg.get("date")

        body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                body = part.get_payload(decode=True).decode(errors="ignore")
                break

        emails.append({
            "id": eid.decode(),
            "from": sender,
            "to": to_addr,                
            "subject": subject or "(No Subject)",
            "date": date,
            "body": body or "<i>No content</i>"
})

    mail.logout()
    return emails