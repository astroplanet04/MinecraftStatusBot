from flask import Flask
from mcstatus import MinecraftServer
import requests
import os

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
        print("Nessun ID messaggio da eliminare")
        return

    # L'URL deve togliere la parte "/api/webhooks" per eliminare messaggi
    # Discord webhook elimina messaggi con: https://discord.com/api/webhooks/{webhook.id}/{webhook.token}/messages/{msg.id}
    # Quindi usiamo direttamente WEBHOOK_URL + "/messages/{msg_id}"

    url = f"{WEBHOOK_URL}/messages/{msg_id}"
    response = requests.delete(url)
    if response.status_code == 204:
        print(f"Messaggio eliminato con successo (ID: {msg_id})")
    else:
        print(f"Errore eliminazione messaggio {msg_id}: {response.status_code} - {response.text}")

def send_new_message(status_online, players_online, players_max):
    status_emoji = "🟢 Online" if status_online else "🔴 Offline"
    players_value = f"{players_online}/{players_max}" if status_online else "0/0"

    embed = {
        "title": "BREVTH Alpha v1.0.6                   1.21.5 & ʙᴇᴅʀᴏᴄᴋ ꜱᴜᴘᴘᴏʀᴛ | ᴅᴜᴇʟꜱ &",
        "description": "This server has many modes: bedwars, skywars, skyblock, oneblock and much more... lots of fun!",
        "color": 0x1abc9c if status_online else 0xe74c3c,
        "thumbnail": {"url": "https://i.postimg.cc/63jfbpjq/40ddf8da-3d69-489e-a338-314a3e6984c3.png"},
        "fields": [
            {"name": "Status", "value": status_emoji, "inline": True},
            {"name": "Address:Port", "value": f"{SERVER_ADDRESS}:{SERVER_PORT}", "inline": True},
            {"name": "Country", "value": ":flag_eu: EU", "inline": True},
            {"name": "Game", "value": "Minecraft", "inline": True},
            {"name": "Players Online", "value": players_value, "inline": True}
        ]
    }

    data = {"embeds": [embed]}
    # Per ottenere la risposta con id messaggio serve ?wait=true
    response = requests.post(WEBHOOK_URL + "?wait=true", json=data)
    if response.status_code in (200, 201):
        try:
            msg_id = response.json().get("id")
            if msg_id:
                salva_id_messaggio(msg_id)
            print(f"Messaggio inviato con successo, ID salvato: {msg_id}")
        except Exception as e:
            print("Errore parsing risposta JSON:", e)
    else:
        print(f"Errore invio messaggio: {response.status_code} - {response.text}")

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
        print(f"Errore controllo server: {e}")
        status_online = False
        players_online = 0
        players_max = 0

    # Elimina vecchio messaggio, invia nuovo
    delete_message()
    send_new_message(status_online, players_online, players_max)

    return "Status inviato a Discord!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
