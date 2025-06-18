from flask import Flask
from mcstatus import MinecraftServer
import requests
import os

app = Flask(__name__)

# === Configuration ===
SERVER_ADDRESS = "mc.brevthcraft.net"
SERVER_PORT = 25565
WEBHOOK_URL = "https://discord.com/api/webhooks/1384164764883619922/wkmz0UCq36CgUetARP2nLyXJamZddxwNd_1MndGyx4tZMkiREXbi7_dZ57P-2Rq8gJGo"
MESSAGE_ID_FILE = "message_id.txt"

# === Utility functions ===
def salva_id_messaggio(msg_id):
    with open(MESSAGE_ID_FILE, "w") as f:
        f.write(str(msg_id))

def leggi_id_messaggio():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            return f.read().strip()
    return None

# === Discord Message Management ===
def delete_message():
    msg_id = leggi_id_messaggio()
    if not msg_id:
        print("No message ID to delete.")
        return

    url = f"{WEBHOOK_URL}/messages/{msg_id}"
    response = requests.delete(url)
    if response.status_code == 204:
        print(f"Message deleted successfully (ID: {msg_id})")
    else:
        print(f"Error deleting message {msg_id}: {response.status_code} - {response.text}")

def send_new_message(status_online, players_online, players_max):
    status_emoji = "🟢 Online" if status_online else "🔴 Offline"
    players_value = f"{players_online}/{players_max}" if status_online else "0/0"

    embed = {
        "title": "BREVTH Alpha v1.0.6   |   1.21.5 + Bedrock Support   |   Duels & More",
        "description": "This server features exciting modes such as **BedWars**, **SkyWars**, **SkyBlock**, **OneBlock**, and much more... Join for endless fun! 🎮",
        "color": 0x1abc9c if status_online else 0xe74c3c,
        "thumbnail": {"url": "https://i.postimg.cc/63jfbpjq/40ddf8da-3d69-489e-a338-314a3e6984c3.png"},
        "fields": [
            {"name": "Status", "value": status_emoji, "inline": True},
            {"name": "Address:Port", "value": f"`{SERVER_ADDRESS}:{SERVER_PORT}`", "inline": True},
            {"name": "Region", "value": ":flag_eu: Europe", "inline": True},
            {"name": "Game", "value": "Minecraft", "inline": True},
            {"name": "Players Online", "value": players_value, "inline": True},
            {"name": "Version", "value": "`1.21.5 + Bedrock`", "inline": True}
        ],
    "image": {
        "url": "https://i.postimg.cc/cHPwNhrY/provalogobrevthcraft.png"  # qui metti il banner grosso sotto
    },
    "footer": {
        "text": "BrevthCraft Network • Auto Status Bot"
    }
}

    data = {"embeds": [embed]}
    response = requests.post(WEBHOOK_URL + "?wait=true", json=data)
    if response.status_code in (200, 201):
        try:
            msg_id = response.json().get("id")
            if msg_id:
                salva_id_messaggio(msg_id)
            print(f"Message sent successfully, ID saved: {msg_id}")
        except Exception as e:
            print("Error parsing JSON response:", e)
    else:
        print(f"Error sending message: {response.status_code} - {response.text}")

# === Web Route ===
@app.route("/", methods=["GET"])
def check_server():
    try:
        server = MinecraftServer.lookup(f"{SERVER_ADDRESS}:{SERVER_PORT}")
        status = server.status()
        status_online = True
        players_online = status.players.online
        players_max = status.players.max
        print(f"Server online: {players_online}/{players_max}")
    except Exception as e:
        print(f"Error checking server: {e}")
        status_online = False
        players_online = 0
        players_max = 0

    delete_message()
    send_new_message(status_online, players_online, players_max)

    return "Status sent to Discord!", 200

# === App Runner ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
