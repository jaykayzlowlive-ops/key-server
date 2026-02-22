from flask import Flask, request, jsonify
import requests
import os
import random
import string

app = Flask(__name__)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# เก็บ key -> hwid
keys = {}

# =========================
# 🔐 สร้างคีย์
# =========================

def generate_key():
    chars = string.ascii_uppercase + string.digits
    return "-".join(
        "".join(random.choice(chars) for _ in range(4))
        for _ in range(3)
    )

def create_keys(amount=25):
    new_keys = []

    for _ in range(amount):
        key = generate_key()
        keys[key] = None
        new_keys.append(f"{key} :")

    send_webhook("🔐 NEW KEYS\n```\n" + "\n".join(new_keys) + "\n```")

# =========================
# 📩 ส่ง Webhook
# =========================

def send_webhook(message):
    if not WEBHOOK_URL:
        print("WEBHOOK_URL NOT SET")
        return

    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print("WEBHOOK ERROR:", e)

# =========================
# 🌐 ROUTES
# =========================

@app.route("/")
def home():
    return "Key Server Running"

@app.route("/health")
def health():
    return "OK"

@app.route("/createkeys")
def create_keys_route():
    create_keys(25)
    return "Created 25 Keys"

# =========================
# 🔐 VERIFY
# =========================

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json

    if not data:
        return jsonify({"status": "error", "message": "No JSON received"})

    key = data.get("key")
    hwid = data.get("hwid")

    if not key or not hwid:
        return jsonify({"status": "error", "message": "Missing key or hwid"})

    if key not in keys:
        return jsonify({"status": "invalid"})

    # bind ครั้งแรก
    if keys[key] is None:
        keys[key] = hwid
        send_webhook(f"🔐 First Bind\nKey: {key}\nHWID: {hwid}")
        return jsonify({"status": "bind_success"})

    # ใช้เครื่องเดิม
    if keys[key] == hwid:
        send_webhook(f"✅ Login Success\nKey: {key}")
        return jsonify({"status": "ok"})

    # เครื่องไม่ตรง
    send_webhook(f"❌ HWID Mismatch\nKey: {key}")
    return jsonify({"status": "hwid_mismatch"})

# =========================
# 🔧 FIX HWID (ผ่าน Webhook)
# =========================

@app.route("/fixhwid", methods=["POST"])
def fix_hwid():
    data = request.json

    key = data.get("key")
    new_hwid = data.get("new_hwid")

    if not key or not new_hwid:
        return jsonify({"status": "error", "message": "Missing key or new_hwid"})

    if key not in keys:
        return jsonify({"status": "invalid_key"})

    keys[key] = new_hwid

    send_webhook(f"🛠 FIX HWID\nKey: {key}\nNew HWID: {new_hwid}")

    return jsonify({"status": "hwid_updated"})

# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
