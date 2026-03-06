import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient

app = Flask(__name__) # Flask otomatik olarak 'templates' klasörüne bakar
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

client = TikTokLiveClient(unique_id="@mylevelupo")

@app.route('/')
def index():
    return render_template('Host.html')

@app.route('/remote')
def remote_page():
    return render_template('Remote.html')

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