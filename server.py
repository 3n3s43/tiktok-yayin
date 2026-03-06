import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

client = TikTokLiveClient(unique_id="@mylevelupo")

# HATALI OLAN KISIM DÜZELTİLDİ:
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    socketio.emit('tiktok_gift_alert', {
        'user': event.user.unique_id,
        'gift_name': event.gift.name,
        'diamonds': event.gift.diamond_count
    })

def start_tiktok():
    try:
        client.run()
    except Exception as e:
        print(f"TikTok Error: {e}")

socketio.start_background_task(start_tiktok)

@app.route('/')
def index(): return send_from_directory('.', 'Host.html')

@app.route('/remote')
def remote_page(): return send_from_directory('.', 'Remote.html')

@app.route('/<path:path>')
def static_files(path): return send_from_directory('.', path)

@socketio.on('execute_visual')
def handle_visual(data):
    emit('execute_visual', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)