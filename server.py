import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient

app = Flask(__name__)
CORS(app)
# async_mode='eventlet' loglardaki o socket hatalarını minimize eder
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

def get_file_content(filename):
    try:
        # Büyük/Küçük harf duyarlı dosya okuma
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
    # Loglara ne yaptığımızı yazalım ki takip edebilelim
    print(f"DEBUG: Gelen Komut -> {data.get('action')}")
    
    if data.get('action') == 'manage_slot' and data.get('username'):
        target_user = data.get('username').strip().replace('@', '')
        print(f"DEBUG: TikTok Sorgusu Baslatildi: {target_user}")
        
        try:
            # Her aramada yepyeni bir client (Connector mantığı)
            search_client = TikTokLiveClient(unique_id=f"@{target_user}")
            user_info = search_client.fetch_user_info()
            
            data['name'] = user_info.nickname # TikTok'taki süslü isim
            data['avatar'] = user_info.avatar_thumb.url_list[0] # Profil resmi
            print(f"DEBUG: {target_user} Basariyla Oturtuldu!")
            
        except Exception as e:
            print(f"DEBUG: TikTok Hatasi: {e}")
            data['name'] = target_user
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
    
    emit('execute_visual', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)