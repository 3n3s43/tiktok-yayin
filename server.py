import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ANA BAĞLANTI: Yayınına bir kez bağlanır ve kopmaz
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
    print(f"DEBUG: Komut Alindi -> {data.get('action')}")
    
    if data.get('action') == 'manage_slot' and data.get('username'):
        target = data.get('username').strip().replace('@', '')
        
        try:
            # DİĞER PROJEDEKİ SIR: fetch_user_info yerine yayındaki aktif veriyi kullanırız
            # Eğer bu metod hata verirse, TikTok sunucusu Render'ı bloklamış demektir.
            user = tiktok_client.fetch_user_info(target)
            data['name'] = user.nickname
            data['avatar'] = user.avatar_thumb.url_list[0]
            print(f"DEBUG: {target} Oturtuldu (Gerçek Bilgi)")
        except Exception as e:
            print(f"DEBUG: TikTok Veri Çekme Hatası: {e}")
            data['name'] = target
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
            
    emit('execute_visual', data, broadcast=True)

# TikTok bağlantısını arka planda başlat
@tiktok_client.on("connect")
def on_connect(_):
    print("TikTok Yayınına Bağlanıldı!")

if __name__ == '__main__':
    # TikTok'u durdurmadan çalıştır
    eventlet.spawn(tiktok_client.run)
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)