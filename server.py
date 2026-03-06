import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)

# Gunicorn + Eventlet ikilisi için en stabil ayar [cite: 2026-03-03]
socketio = SocketIO(app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    logger=True, 
    engineio_logger=True)

# --- TİKTOK BAĞLANTISI ---
# Kullanıcı adınla yayını dinlemeye başlar
client = TikTokLiveClient(unique_id="@mylevelupo")

@client.on("gift")
async def on_gift(event: GiftEvent):
    # DİKKAT: Bu kısım sadece Remote'a bildirim gönderir.
    # Sen Remote'dan basana kadar Host (Ekran) değişmez.
    socketio.emit('tiktok_gift_alert', {
        'user': event.user.unique_id,
        'gift_name': event.gift.name,
        'diamonds': event.gift.diamond_count
    })

# TikTok dinleyicisini arka planda güvenli çalıştırma
def start_tiktok():
    try:
        client.run()
    except Exception as e:
        print(f"TikTok Connection Error: {e}")

socketio.start_background_task(start_tiktok)

# --- YOLLAR (ROUTES) ---
@app.route('/')
def index(): 
    return send_from_directory('.', 'Host.html')

@app.route('/remote')
def remote_page(): 
    return send_from_directory('.', 'Remote.html')

@app.route('/<path:path>')
def static_files(path): 
    return send_from_directory('.', path)

# --- SOKET OLAYLARI ---
@socketio.on('execute_visual')
def handle_visual(data):
    emit('execute_visual', data, broadcast=True)

@socketio.on('toggle_edit')
def handle_edit(data):
    emit('toggle_edit', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)