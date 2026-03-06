import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Yayınına bağlanacak ana client
tiktok_client = TikTokLiveClient(unique_id="@mylevelupo")

def get_file_content(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Dosya bulunamadi."

@app.route('/')
def index():
    return Response(get_file_content("Host.html"), mimetype='text/html')

@app.route('/remote')
def remote_page():
    return Response(get_file_content("Remote.html"), mimetype='text/html')

@socketio.on('execute_visual')
def handle_visual(data):
    if data.get('action') == 'manage_slot' and data.get('username'):
        target = data.get('username').strip().replace('@', '')
        print(f"DEBUG: Sorgu Baslatildi -> {target}")
        
        try:
            # YENİ VERSİYON ÇÖZÜMÜ: fetch_user_info yerine get_user_info dene
            # Eğer o da olmazsa direkt web_proxy üzerinden çekmeyi dener
            try:
                user = tiktok_client.web_proxy.get_user_info(target)
            except:
                # Alternatif metod
                user = tiktok_client.get_user_info(target)
            
            data['name'] = user.nickname
            data['avatar'] = user.avatar_thumb.url_list[0]
            print(f"DEBUG: {target} basariyla bulundu.")
        except Exception as e:
            # Hata ne olursa olsun logla ama ekrana manuel ismi bas
            print(f"DEBUG: TikTok Veri Çekme Hatası: {e}")
            data['name'] = target
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
            
    emit('execute_visual', data, broadcast=True)

@tiktok_client.on(ConnectEvent)
def on_connect(event: ConnectEvent):
    print("TikTok Yayınına Bağlanıldı!")

if __name__ == '__main__':
    # TikTok istemcisini ayrı bir thread'de başlat
    eventlet.spawn(tiktok_client.run)
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)