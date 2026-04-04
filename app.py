from flask import Flask, jsonify, request, send_from_directory

from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Use Render's persistent disk or tmp for database
DB_PATH = os.environ.get('DATABASE_PATH', 'emails.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender TEXT,
                  subject TEXT,
                  body TEXT,
                  received_time TEXT,
                  is_read BOOLEAN DEFAULT 0)''')
    conn.commit()
    conn.close()

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Receive emails from Make.com"""
    try:
        data = request.get_json()
        
        sender = data.get('sender', 'Unknown')
        subject = data.get('subject', 'No Subject')
        body = data.get('body', '')
        received_time = data.get('received_time', datetime.now().isoformat())
        
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO emails (sender, subject, body, received_time) VALUES (?, ?, ?, ?)",
                 (sender, subject, body[:10000], received_time))
        conn.commit()
        
        # Get the ID of inserted email
        email_id = c.lastrowid
        conn.close()
        
        print(f"[{datetime.now()}] Webhook received: {subject[:50]}... (ID: {email_id})")
        return jsonify({"status": "success", "id": email_id}), 200
        
    except Exception as e:
        print(f"[{datetime.now()}] Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/emails')
def get_emails():
    """Get all emails"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, sender, subject, received_time, is_read FROM emails ORDER BY received_time DESC")
        emails = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(emails)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emails/<int:id>')
def get_email_body(id):
    """Get full email body"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM emails WHERE id = ?", (id,))
        row = c.fetchone()
        
        if row:
            c.execute("UPDATE emails SET is_read = 1 WHERE id = ?", (id,))
            conn.commit()
            email = dict(row)
            conn.close()
            return jsonify(email)
        else:
            conn.close()
            return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Serve the main page"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Public Mail Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            color: rgba(255,255,255,0.8);
            text-align: center;
            margin-bottom: 30px;
        }
        .email-list {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .email-item {
            padding: 20px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .email-item:hover {
            background: #f8f9ff;
            transform: translateX(5px);
        }
        .email-item.unread {
            border-left: 4px solid #667eea;
            background: #f0f4ff;
        }
        .email-meta {
            flex: 1;
        }
        .sender {
            font-weight: bold;
            color: #333;
            font-size: 1.1em;
        }
        .subject {
            color: #666;
            margin-top: 5px;
        }
        .time {
            color: #999;
            font-size: 0.9em;
            white-space: nowrap;
        }
        .badge {
            background: #667eea;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75em;
            margin-left: 10px;
        }
        .empty {
            padding: 60px;
            text-align: center;
            color: #999;
        }
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.7);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .modal-overlay.active {
            display: flex;
        }
        .modal {
            background: white;
            border-radius: 15px;
            max-width: 800px;
            width: 100%;
            max-height: 90vh;
            overflow: hidden;
            animation: slideUp 0.3s ease;
        }
        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            position: relative;
        }
        .modal-body {
            padding: 20px;
            overflow-y: auto;
            max-height: 60vh;
            line-height: 1.6;
            white-space: pre-wrap;
            font-family: monospace;
            background: #f8f9fa;
        }
        .close-btn {
            position: absolute;
            top: 15px;
            right: 20px;
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            width: 35px;
            height: 35px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.2em;
        }
        .status-bar {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 12px 20px;
            border-radius: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 100;
        }
        .pulse {
            width: 10px;
            height: 10px;
            background: #4ade80;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📧 Public Mail Portal</h1>
        <div class="subtitle">Real-time email display • No login required • 24/7 Live</div>
        
        <div class="email-list" id="emailList">
            <div class="empty">
                <h3>Waiting for emails...</h3>
                <p>Send a test email to see it appear here</p>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="modal" onclick="closeModal(event)">
        <div class="modal" onclick="event.stopPropagation()">
            <div class="modal-header">
                <button class="close-btn" onclick="closeModal()">×</button>
                <div id="modalSender"></div>
                <div id="modalSubject" style="margin-top: 10px; opacity: 0.9;"></div>
                <div id="modalTime" style="margin-top: 5px; font-size: 0.9em; opacity: 0.8;"></div>
            </div>
            <div class="modal-body" id="modalBody"></div>
        </div>
    </div>

    <div class="status-bar">
        <div class="pulse"></div>
        <span>Live • Auto-refresh ON</span>
    </div>

    <script>
        const API_URL = window.location.origin + "/api";
        
        async function loadEmails() {
            try {
                const res = await fetch(`${API_URL}/emails`);
                const emails = await res.json();
                
                const list = document.getElementById("emailList");
                if (emails.length === 0) {
                    list.innerHTML = `<div class="empty"><h3>No emails yet</h3><p>The inbox is empty. Send a test email to get started!</p></div>`;
                    return;
                }
                
                list.innerHTML = emails.map(email => `
                    <div class="email-item ${!email.is_read ? "unread" : ""}" onclick="openEmail(${email.id})">
                        <div class="email-meta">
                            <div class="sender">
                                ${escapeHtml(email.sender)}
                                ${!email.is_read ? "<span class=\"badge\">NEW</span>" : ""}
                            </div>
                            <div class="subject">${escapeHtml(email.subject)}</div>
                        </div>
                        <div class="time">${formatTime(email.received_time)}</div>
                    </div>
                `).join("");
            } catch (err) {
                console.error("Failed to load emails:", err);
            }
        }
        
        async function openEmail(id) {
            try {
                const res = await fetch(`${API_URL}/emails/${id}`);
                const email = await res.json();
                
                document.getElementById("modalSender").innerHTML = `<strong>From:</strong> ${escapeHtml(email.sender)}`;
                document.getElementById("modalSubject").textContent = email.subject;
                document.getElementById("modalTime").textContent = new Date(email.received_time).toLocaleString();
                document.getElementById("modalBody").textContent = email.body || "[No content]";
                document.getElementById("modal").classList.add("active");
                
                loadEmails();
            } catch (err) {
                alert("Failed to load email");
            }
        }
        
        function closeModal(e) {
            if (!e || e.target.id === "modal") {
                document.getElementById("modal").classList.remove("active");
            }
        }
        
        function escapeHtml(text) {
            if (!text) return "";
            const div = document.createElement("div");
            div.textContent = text;
            return div.innerHTML;
        }
        
        function formatTime(isoString) {
            const date = new Date(isoString);
            const now = new Date();
            const diff = (now - date) / 1000;
            
            if (diff < 60) return "Just now";
            if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
            if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
            return date.toLocaleDateString();
        }
        
        setInterval(loadEmails, 5000);
        loadEmails();
        
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") closeModal();
        });
    </script>
</body>
</html>'''

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
