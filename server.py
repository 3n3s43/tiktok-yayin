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

# TikTok yayınına bağlanacak ana istemci (Puan takibi için)
main_client = TikTokLiveClient(unique_id="@mylevelupo")

# Dosyaları fiziksel olarak okuyan yardımcı fonksiyon (Not Found hatasını bitiren yöntem)
def get_file_content(filename):
    try:
        # GitHub'daki büyük harf kullanımına dikkat ederek okur
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Dosya okuma hatasi: {str(e)}"

@app.route('/')
def index():
    # Host.html dosyasını ana dizinden gönderir
    return Response(get_file_content("Host.html"), mimetype='text/html')

@app.route('/remote')
def remote_page():
    # Remote.html dosyasını ana dizinden gönderir
    return Response(get_file_content("Remote.html"), mimetype='text/html')

@socketio.on('execute_visual')
def handle_visual(data):
    # Kullanıcıyı koltuğa oturtma işlemi
    if data.get('action') == 'manage_slot' and data.get('username'):
        target_user = data.get('username').strip().replace('@', '')
        print(f"DEBUG: TikTok'tan araniyor: {target_user}")
        
        try:
            # Diğer projendeki gibi her aramada taze bir sorgu açar
            search_client = TikTokLiveClient(unique_id=f"@{target_user}")
            user_info = search_client.fetch_user_info()
            
            # TikTok'tan gelen verileri pakete ekle
            data['name'] = user_info.nickname # Süslü takma ad
            data['avatar'] = user_info.avatar_thumb.url_list[0] # Profil resmi
            print(f"DEBUG: {user_info.nickname} bulundu ve Host'a iletiliyor.")
            
        except Exception as e:
            print(f"DEBUG: TikTok API Hatasi: {e}")
            # Hata durumunda kumandada yazılan ismi kullanır, varsayılan resim atar
            data['name'] = target_user
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
    
    # Tüm veriyi (puan, isim, resim vb.) hem Host'a hem Remote'a gönderir
    emit('execute_visual', data, broadcast=True)

if __name__ == '__main__':
    # Render'ın atadığı portu kullanır
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)