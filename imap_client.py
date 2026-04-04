import imaplib
import email
from email.header import decode_header

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

GMAIL_USER = "atmailpdt@gmail.com"
APP_PASSWORD = "siqovmkceoelhqjd"

def decode(value):
    if value:
        parts = decode_header(value)
        return ''.join(
            str(p[0], p[1] or 'utf-8') if isinstance(p[0], bytes) else str(p[0])
            for p in parts
        )
    return ""

def fetch_emails(limit=20):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(GMAIL_USER, APP_PASSWORD)
    mail.select("inbox")

    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()[-limit:]

    emails = []

    for eid in reversed(email_ids):
        _, msg_data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        subject = decode(msg["subject"])
        sender = decode(msg["from"])
        date = msg["date"]

        html_body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html_body = part.get_payload(decode=True).decode(errors="ignore")

        emails.append({
            "id": eid.decode(),
            "from": sender,
            "subject": subject,
            "date": date,
            "body": html_body
        })

        # Mark as seen
        mail.store(eid, '+FLAGS', '\\Seen')

    mail.logout()
    return emails

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_emails(limit=20):
    logger.info("Connecting to Gmail IMAP")
    ...
    logger.info(f"Found {len(email_ids)} unread emails")
    ...