import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# TikTok istemcisi - sadece bilgi sorgulamak için de kullanılır
client = TikTokLiveClient(unique_id="@mylevelupo")

@socketio.on('execute_visual')
def handle_visual(data):
    # 'username' anahtarı üzerinden gelen ismi TikTok'ta arıyoruz
    if data.get('action') == 'manage_slot' and data.get('username'):
        target_user = data.get('username').replace('@', '') # @ varsa temizle
        print(f"DEBUG: TikTok'ta aranıyor: {target_user}")
        
        try:
            # TikTok'tan profil bilgilerini çek
            user_info = client.fetch_user_info(target_user)
            data['name'] = user_info.nickname  # TikTok'taki süslü adı
            data['avatar'] = user_info.avatar_thumb.url_list[0] # Gerçek profil resmi
            print(f"DEBUG: Bulundu! Nick: {user_info.nickname}")
        except Exception as e:
            print(f"DEBUG: TikTok hatası: {e}")
            # Bulamazsa senin yazdığın ismi ve boş resmi kullanır
            data['name'] = target_user
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
    
    emit('execute_visual', data, broadcast=True)

@app.route('/')
def index(): return send_from_directory('.', 'Host.html')

@app.route('/remote')
def remote_page(): return send_from_directory('.', 'Remote.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)