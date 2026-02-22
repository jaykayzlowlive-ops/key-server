from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

WEBHOOK_URL = os.getenv("https://discordapp.com/api/webhooks/1475128103884816499/4cqVrvWskDy2L9NWeYNzTahssKotueBCHdg4OFZGfu46E0rb4cz4_pIPdEgjFFQzw1E6")

# ตัวอย่างเก็บ key (ไว้เทสก่อน)
keys = {
    "1234": None,
    "VIP999": None
}

@app.route("/health")
def health():
    return "OK"


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
