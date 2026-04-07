# 📬 Mail Portal (IMAP-based)

A lightweight **Gmail-like Mail Portal** built using **Flask** and **Gmail IMAP**, deployed on **Render**. This portal allows remote users to view **all emails** from a Gmail inbox in a clean, expandable UI similar to Gmail.

---

## ✨ Features

- Fetch **ALL emails** from Gmail (not just unread)
- Gmail-style expand/collapse UI
- Displays **From / To / Date / Subject / Body**
- Manual **Refresh** button
- Shows last refresh time in **IST (Indian Standard Time)**
- Remote access via Render deployment
- No Gmail UI automation (uses IMAP)

---

## 🏗️ Tech Stack

- **Backend:** Python, Flask
- **Mail Access:** Gmail IMAP
- **Frontend:** HTML + CSS (Jinja templates)
- **Server:** Gunicorn
- **Hosting:** Render

---

## 📁 Project Structure

```
mail-portal/
├── app.py                # Flask application
├── imap_client.py        # IMAP email fetch logic
├── requirements.txt      # Python dependencies
└── templates/
    └── inbox.html        # Gmail-like inbox UI
```

---

## 🔐 Gmail Account Setup

### 1. Use a Dedicated Gmail Account

Recommended for testing/automation:
```
example.mail.portal@gmail.com
```

### 2. Enable IMAP

Gmail → Settings → See all settings → Forwarding and POP/IMAP
- ✅ Enable IMAP

### 3. Enable 2-Step Verification

Google Account → Security → Enable **2-Step Verification**

### 4. Create App Password

Google Account → Security → App passwords
- App: **Mail**
- Device: **Other (Mail Portal)**

Save the generated **16-character app password**.

---

## ⚙️ Configuration (Render)

### Environment Variables

Set the following in **Render → Environment → Environment Variables**:

| Key | Value |
|----|-------|
| GMAIL_USER | your_gmail@gmail.com |
| GMAIL_APP_PASSWORD | your_app_password |

⚠️ Do NOT hardcode credentials in the repository.

---

## 🚀 Deployment on Render

1. Push the project to GitHub
2. Create a **Web Service** on Render
3. Runtime: **Python 3**
4. Build Command:
   ```bash
   pip install -r requirements.txt
   ```
5. Start Command:
   ```bash
   gunicorn app:app
   ```
6. Deploy 🎉

---

## 🔄 Refresh Mechanism

- Clicking **Refresh** sends a new `GET /` request
- Flask re-fetches emails via IMAP
- Newly arrived emails appear immediately
- Refresh timestamp updates automatically

---

## 🕒 IST Time Handling

The backend converts time to IST using:

```python
refreshed = datetime.utcnow().astimezone(
    timezone(timedelta(hours=5, minutes=30))
).strftime("%Y-%m-%d %H:%M:%S IST")
```

---

## ✅ Health Check Endpoint

```
GET /health
```

Response:
```json
{"status": "UP"}
```

---

## ⚠️ Notes & Limitations

- Suitable for internal tools / test portals
- IMAP credentials are shared backend secrets
- For production-grade systems, consider **Gmail API (OAuth)**

---

## 🛣️ Future Enhancements

- Search & filtering
- Pagination
- Auto-refresh
- Attachment previews
- DB caching (Postgres on Render)

---

## ✅ Summary

This project provides a simple, reliable Gmail-like web interface to view emails using Gmail IMAP, deployed cleanly on Render and suitable for internal or test usage.

📬 Happy mailing!
