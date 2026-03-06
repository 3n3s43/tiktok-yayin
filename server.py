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

client = TikTokLiveClient(unique_id="@mylevelupo")

# Dosyayı manuel okuyan yardımcı fonksiyon
def get_file_content(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Dosya okuma hatasi: {str(e)}"

@app.route('/')
def index():
    # Host.html dosyasını direkt oku ve gönder
    content = get_file_content("Host.html")
    return Response(content, mimetype='text/html')

@app.route('/remote')
def remote_page():
    # Remote.html dosyasını direkt oku ve gönder
    content = get_file_content("Remote.html")
    return Response(content, mimetype='text/html')

@socketio.on('execute_visual')
def handle_visual(data):
    if data.get('action') == 'manage_slot' and data.get('username'):
        target_user = data.get('username').replace('@', '')
        try:
            user_info = client.fetch_user_info(target_user)
            data['name'] = user_info.nickname
            data['avatar'] = user_info.avatar_thumb.url_list[0]
        except Exception as e:
            data['name'] = target_user
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"
    
    emit('execute_visual', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)