from flask import Flask, request, jsonify
import requests
import os
import random
import string

app = Flask(__name__)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# โครงสร้าง:
# key: { "hwid": None, "message_id": None }
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
    if not WEBHOOK_URL:
        print("WEBHOOK_URL NOT SET")
        return

    for _ in range(amount):
        key = generate_key()

        try:
            response = requests.post(
                WEBHOOK_URL + "?wait=true",
                json={"content": f"{key} :"}
            )

            if response.status_code == 200:
                message_data = response.json()

                keys[key] = {
                    "hwid": None,
                    "message_id": message_data["id"]
                }

            else:
                print("CREATE KEY ERROR:", response.text)

        except Exception as e:
            print("CREATE KEY EXCEPTION:", e)


# =========================
# ✏️ แก้ข้อความ key
# =========================

def edit_key_message(key):
    if key not in keys:
        return

    data = keys[key]

    if not data["message_id"]:
        print("NO MESSAGE ID FOR KEY:", key)
        return

    try:
        webhook_part = WEBHOOK_URL.split("/api/webhooks/")[1]
        webhook_id, webhook_token = webhook_part.split("/")

        edit_url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}/messages/{data['message_id']}"

        new_content = f"{key} : {data['hwid'] if data['hwid'] else ''}"

        response = requests.patch(edit_url, json={
            "content": new_content
        })

        if response.status_code != 200:
            print("EDIT ERROR:", response.text)

    except Exception as e:
        print("EDIT EXCEPTION:", e)


# =========================
# 📩 ส่ง log
# =========================

def send_log(message):
    if not WEBHOOK_URL:
        print("WEBHOOK_URL NOT SET")
        return

    try:
        response = requests.post(WEBHOOK_URL, json={"content": message})
        if response.status_code != 204 and response.status_code != 200:
            print("LOG ERROR:", response.text)
    except Exception as e:
        print("LOG EXCEPTION:", e)


# =========================
# 🌐 ROUTES
# =========================

@app.route("/health")
def health():
    return "OK"


@app.route("/createkeys")
def create_keys_route():
    create_keys(25)
    return "Created 25 Keys"


@app.route("/verify", methods=["POST"])
def verify():
    try:
        data = request.json

        if not data:
            return jsonify({"status": "error"})

        key = data.get("key")
        hwid = data.get("hwid")

        if key not in keys:
            return jsonify({"status": "invalid"})

        # bind ครั้งแรก
        if keys[key]["hwid"] is None:
            keys[key]["hwid"] = hwid
            edit_key_message(key)
            send_log(f"🔐 First Bind\nKey: {key}\nHWID: {hwid}")
            return jsonify({"status": "bind_success"})

        # ใช้เครื่องเดิม
        if keys[key]["hwid"] == hwid:
            send_log(f"✅ Login Success\nKey: {key}")
            return jsonify({"status": "ok"})

        send_log(f"❌ HWID Mismatch\nKey: {key}")
        return jsonify({"status": "hwid_mismatch"})

    except Exception as e:
        print("VERIFY ERROR:", e)
        return jsonify({"status": "server_error"})


@app.route("/fixhwid", methods=["POST"])
def fix_hwid():
    try:
        data = request.json
        key = data.get("key")
        new_hwid = data.get("hwid")

        if key not in keys:
            return jsonify({"status": "invalid_key"})

        keys[key]["hwid"] = new_hwid
        edit_key_message(key)

        send_log(f"🛠 FIX HWID\nKey: {key}\nNew HWID: {new_hwid}")

        return jsonify({"status": "hwid_updated"})

    except Exception as e:
        print("FIX ERROR:", e)
        return jsonify({"status": "server_error"})


# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
