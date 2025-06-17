from flask import Flask
from mcstatus import MinecraftServer
import requests
import os
from datetime import datetime

app = Flask(__name__)

SERVER_ADDRESS = "mc.brevthcraft.net"
SERVER_PORT = 25565

WEBHOOK_URL = "https://discord.com/api/webhooks/1384164764883619922/wkmz0UCq36CgUetARP2nLyXJamZddxwNd_1MndGyx4tZMkiREXbi7_dZ57P-2Rq8gJGo"
MESSAGE_ID_FILE = "message_id.txt"

def salva_id_messaggio(msg_id):
    with open(MESSAGE_ID_FILE, "w") as f:
        f.write(str(msg_id))

def leggi_id_messaggio():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            return f.read().strip()
    return None

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
    status_emoji = "🟢 **Online**" if status_online else "🔴 **Offline**"
    players_value = f"{players_online}/{players_max}" if status_online else "0/0"

    embed = {
        "title": "**🌐 BREVTH Alpha v1.0.6**",
        "description": "🎮 **Minecraft Server Status Update**\nJoin and have fun with Bedwars, Skywars, Skyblock, Oneblock, and more!",
        "color": 0x00ff00 if status_online else 0xff0000,
        "thumbnail": {"url": "https://i.postimg.cc/63jfbpjq/40ddf8da-3d69-489e-a338-314a3e6984c3.png"},
        "fields": [
    {"name": "📡 Status", "value": status_emoji, "inline": True},
    {"name": "\u200b", "value": "\u200b", "inline": True},  # campo vuoto per spazio

    {"name": "🖥️ Address:Port", "value": f"`{SERVER_ADDRESS}:{SERVER_PORT}`", "inline": True},
    {"name": "\u200b", "value": "\u200b", "inline": True},

    {"name": "🌍 Region", "value": ":flag_eu: Europe", "inline": True},
    {"name": "\u200b", "value": "\u200b", "inline": True},

    {"name": "🎮 Game", "value": "Minecraft", "inline": True},
    {"name": "\u200b", "value": "\u200b", "inline": True},

    {"name": "👥 Players Online", "value": players_value, "inline": True},
    {"name": "\u200b", "value": "\u200b", "inline": True},

    {"name": "📜 Version", "value": "1.21.5 & Bedrock Support", "inline": True}
],
        "footer": {
            "text": "Last updated: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "icon_url": "https://i.postimg.cc/63jfbpjq/40ddf8da-3d69-489e-a338-314a3e6984c3.png"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "components": [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "style": 5,
                        "label": "🌐 Visit Website",
                        "url": "https://minecraftstatusbot.onrender.com"
                    },
                    {
                        "type": 2,
                        "style": 5,
                        "label": "📜 Server Rules",
                        "url": "https://discord.gg/your-invite-code"
                    }
                ]
            }
        ]
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
            print("Error parsing response JSON:", e)
    else:
        print(f"Error sending message: {response.status_code} - {response.text}")

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
