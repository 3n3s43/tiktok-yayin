import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient

# Mevcut çalışma dizinini netleştiriyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

client = TikTokLiveClient(unique_id="@mylevelupo")

@app.route('/')
def index():
    # Klasör karmaşasını önlemek için tam yol kullanıyoruz
    return send_from_directory(BASE_DIR, 'Host.html')

@app.route('/remote')
def remote_page():
    # DİKKAT: GitHub'daki dosya adın 'Remote.html' ise burası da aynı olmalı
    # Eğer GitHub'da 'remote.html' ise burayı küçük harf yap.
    return send_from_directory(BASE_DIR, 'Remote.html')

@socketio.on('execute_visual')
def handle_visual(data):
    if data.get('action') == 'manage_slot' and data.get('username'):
        target_user = data.get('username').replace('@', '')
        print(f"DEBUG: TikTok sorgusu yapılıyor: {target_user}")
        try:
            user_info = client.fetch_user_info(target_user)
            data['name'] = user_info.nickname
            data['avatar'] = user_info.avatar_thumb.url_list[0]
            print(f"DEBUG: {target_user} bulundu!")
        except Exception as e:
            print(f"DEBUG: TikTok hatası: {e}")
            data['name'] = target_user
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
    
    emit('execute_visual', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)