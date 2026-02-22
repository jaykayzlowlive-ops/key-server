from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔥 ใส่ webhook ผ่าน environment variable
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# ตัวอย่างเก็บ key (เอาไว้เทสก่อน)
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
    key = data.get("key")
    hwid = data.get("hwid")

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
        requests.post(WEBHOOK_URL, json={"content": message})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
