from flask import Flask, request, jsonify
import uuid
import json
import os
from datetime import datetime

app = Flask(__name__)
SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")


def load_sessions():
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_sessions(sessions):
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)


@app.route("/api/create_session", methods=["POST"])
def create_session():
    data = request.get_json() or {}
    platform = data.get("platform")
    username = data.get("username")
    telegram_id = data.get("telegram_id")
    if not platform or not username:
        return jsonify({"error": "platform and username required"}), 400
    sessions = load_sessions()
    session_id = uuid.uuid4().hex
    sessions[session_id] = {
        "platform": platform,
        "username": username,
        "telegram_id": telegram_id,
        "verified": False,
        "created_at": datetime.utcnow().isoformat(),
        "verified_at": None,
    }
    save_sessions(sessions)
    return jsonify({"session_id": session_id})


@app.route("/unlock/<session_id>")
def unlock_page(session_id: str):
    sessions = load_sessions()
    if session_id not in sessions:
        return "<h1>Invalid session</h1>", 404
    s = sessions[session_id]
    # Simple HTML that simulates a login flow and calls /api/verify
    html = f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"> 
    <title>Zoktu — Unlock</title>
  </head>
  <body>
    <h2>Zoktu — Unlock Demo Profile</h2>
    <p>Platform: <strong>{s['platform']}</strong></p>
    <p>Username: <strong>{s['username']}</strong></p>
    <p>Click below to simulate logging into Zoktu and verify this session.</p>
    <button id=\"login\">Simulate login (verify session)</button>
    <div id=\"msg\" style=\"margin-top:12px;color:green\"></div>
    <script>
      document.getElementById('login').addEventListener('click', async function(){{
        try{{
          const r = await fetch('/api/verify', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ session_id: '{session_id}' }})
          }});
          const j = await r.json();
          document.getElementById('msg').innerText = j.message || JSON.stringify(j);
        }}catch(e){{
          document.getElementById('msg').innerText = 'Request failed: ' + e;
        }}
      }});
    </script>
  </body>
</html>"""
    return html


@app.route("/auth")
def auth_page():
    # Support query param guest_id so external site (e.g. https://zoktu.com/auth?guest_id=...) can reuse this verification flow
    session_id = request.args.get("guest_id")
    if not session_id:
        return "<h1>Missing guest_id</h1>", 400
    sessions = load_sessions()
    if session_id not in sessions:
        return "<h1>Invalid guest id</h1>", 404
    s = sessions[session_id]
    # Reuse the same simple HTML UI as /unlock
    html = f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\"> 
    <title>Zoktu — Unlock</title>
  </head>
  <body>
    <h2>Zoktu — Unlock Demo Profile</h2>
    <p>Platform: <strong>{s['platform']}</strong></p>
    <p>Username: <strong>{s['username']}</strong></p>
    <p>Click below to simulate logging into Zoktu and verify this session.</p>
    <button id=\"login\">Simulate login (verify session)</button>
    <div id=\"msg\" style=\"margin-top:12px;color:green\"></div>
    <script>
      document.getElementById('login').addEventListener('click', async function(){{
        try{{
          const r = await fetch('/api/verify', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{ session_id: '{session_id}' }})
          }});
          const j = await r.json();
          document.getElementById('msg').innerText = j.message || JSON.stringify(j);
        }}catch(e){{
          document.getElementById('msg').innerText = 'Request failed: ' + e;
        }}
      }});
    </script>
  </body>
</html>"""
    return html


@app.route("/api/verify", methods=["POST"])
def api_verify():
    data = request.get_json() or {}
    sid = data.get("session_id")
    if not sid:
        return jsonify({"error": "session_id required"}), 400
    sessions = load_sessions()
    if sid not in sessions:
        return jsonify({"error": "unknown session"}), 404
    sessions[sid]["verified"] = True
    sessions[sid]["verified_at"] = datetime.utcnow().isoformat()
    save_sessions(sessions)
    return jsonify({"success": True, "message": "Session verified. Return to Telegram and press 'I've unlocked' to see the profile."})


@app.route("/api/session/<session_id>")
def get_session(session_id: str):
    sessions = load_sessions()
    s = sessions.get(session_id)
    if not s:
        return jsonify({"error": "not found"}), 404
    return jsonify(s)


if __name__ == "__main__":
    # For demo purposes only. Use a proper server behind HTTPS in production.
    app.run(host="0.0.0.0", port=5000, debug=True)
