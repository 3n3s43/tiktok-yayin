import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Socket ayarları en stabil halde
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
    # Remote'tan gelen veriyi doğrudan yayınlıyoruz (Hibrit Sistem)
    print(f"--> Gelen Hazır Paket: {data.get('name')} (Koltuk: {data.get('slot')})")
    emit('execute_visual', data, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)