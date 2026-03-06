import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient

app = Flask(__name__)
CORS(app)
# En uyumlu socket ayarları
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', logger=True, engineio_logger=True)

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
    # Loglarda bu yazıyı görmeliyiz!
    print(f"!!! KOMUT GELDI: {data}")
    
    if data.get('action') == 'manage_slot' and data.get('username'):
        target = data.get('username').strip().replace('@', '')
        
        # TikTok sorgusunu en basit haliyle yapıyoruz
        try:
            # Client'ı sorgu içinde oluşturup hemen kapatmak en garanti yoldur
            client = TikTokLiveClient(unique_id=f"@{target}")
            user_info = client.fetch_user_info() 
            
            data['name'] = user_info.nickname
            data['avatar'] = user_info.avatar_thumb.url_list[0]
            print(f"!!! BULUNDU: {user_info.nickname}")
        except Exception as e:
            print(f"!!! TIKTOK HATASI: {e}")
            data['name'] = target
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
            
    emit('execute_visual', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)