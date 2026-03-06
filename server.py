import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient
# Yeni versiyonlarda bilgi çekmek için bu alt kütüphane gerekebilir
from TikTokLive.types.errors import UserNotFound 

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

def get_file_content(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Dosya hatasi: {str(e)}"

@app.route('/')
def index():
    return Response(get_file_content("Host.html"), mimetype='text/html')

@app.route('/remote')
def remote_page():
    return Response(get_file_content("Remote.html"), mimetype='text/html')

@socketio.on('execute_visual')
def handle_visual(data):
    if data.get('action') == 'manage_slot' and data.get('username'):
        target_user = data.get('username').strip().replace('@', '')
        print(f"DEBUG: TikTok Sorgusu Baslatildi: {target_user}")
        
        try:
            # Hata veren 'fetch_user_info' yerine en güncel arama metodunu kullanıyoruz
            search_client = TikTokLiveClient(unique_id=f"@{target_user}")
            user_data = search_client.get_user_info() # Bazı versiyonlarda 'get_user_info' olur
            
            data['name'] = user_data.nickname
            data['avatar'] = user_data.avatar_thumb.url_list[0]
            print(f"DEBUG: {target_user} bulundu!")
            
        except Exception as e:
            # Eğer 'get_user_info' da hata verirse en garanti yöntem:
            print(f"DEBUG: Birinci yontem basarisiz, alternatif deneniyor: {e}")
            try:
                # Alternatif: Bilgileri doğrudan client üzerinden çekmeyi dene
                info = search_client.fetch_user_info() 
                data['name'] = info.nickname
                data['avatar'] = info.avatar_thumb.url_list[0]
            except:
                data['name'] = target_user
                data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
    
    emit('execute_visual', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)