from flask import Flask, request, jsonify
import requests
import os
import random
import string

app = Flask(__name__)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# เก็บ key
keys = {
    "1234": None,
    "VIP999": None
}

# =========================
# 🔐 สร้างคีย์อัตโนมัติ
# =========================

def generate_key():
    chars = string.ascii_uppercase + string.digits
    return "-".join(
        "".join(random.choice(chars) for _ in range(4))
        for _ in range(3)
    )

def create_keys(amount=25):
    if not WEBHOOK_URL:
        return

    new_keys = []

    for _ in range(amount):
        key = generate_key()
        keys[key] = None
        new_keys.append(f"{key} :")

    content = "🔐 NEW KEYS\n```\n" + "\n".join(new_keys) + "\n```"

    try:
        requests.post(WEBHOOK_URL, json={"content": content})
    except:
        pass

# =========================

@app.route("/health")
def health():
    return "OK"

# 🔥 เรียกสร้างคีย์ผ่านเว็บ
@app.route("/createkeys")
def create_keys_route():
    create_keys(25)
    return "Created 25 Keys"


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
        send_log(f"🔐 First Bind\nKey: {key}\nHWID: {hwid}")
        return jsonify({"status": "bind_success"})

    # ใช้เครื่องเดิม
    if keys[key] == hwid:
        send_log(f"✅ Login Success\nKey: {key}")
        return jsonify({"status": "ok"})

    # เครื่องไม่ตรง
    send_log(f"❌ HWID Mismatch\nKey: {key}")
    return jsonify({"status": "hwid_mismatch"})


def send_log(message):
    if WEBHOOK_URL:
        try:
            requests.post(WEBHOOK_URL, json={"content": message})
        except:
            pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
