import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient

app = Flask(__name__)
CORS(app)
# En uyumlu socket ayarları ve logger açık
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

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
    # Sinyal geldi mi? Kontrol edelim
    print(f"--> KOMUT ALINDI: {data.get('action')}")

    if data.get('action') == 'manage_slot' and data.get('username'):
        target = data.get('username').strip().replace('@', '')
        print(f"--> TIKTOK SORGUSU: {target}")

        try:
            # DİĞER PROJEDEKİ GİZLİ YÖNTEM:
            # Client üzerinden değil, kütüphanenin web modülü üzerinden sorgu
            temp_client = TikTokLiveClient(unique_id=f"@{target}")
            # Yeni versiyonlarda en sağlam bilgi çekme yolu budur:
            user_data = temp_client.web.get_user_info(target)
            
            data['name'] = user_data.nickname
            data['avatar'] = user_data.avatar_thumb.url_list[0]
            print(f"--> BAŞARILI: {user_data.nickname} bulundu!")

        except Exception as e:
            # Eğer yukarıdaki metod hata verirse, en azından manuel ismi ekrana bas
            print(f"--> TIKTOK HATASI (Detay): {str(e)}")
            data['name'] = target
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
    
    # Bilgileri (Gerçek veya Manuel) tüm ekranlara yay
    emit('execute_visual', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)