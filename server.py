import os
from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Render ve benzeri platformlarda kopma olmaması için transports ve async_mode ekledik
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

@app.route('/')
def index(): 
    return send_from_directory('.', 'Host.html')

@app.route('/remote')
def remote_page(): 
    return send_from_directory('.', 'Remote.html')

@app.route('/<path:path>')
def static_files(path): 
    return send_from_directory('.', path)

# 1. ASLAN VE OTURTMA SİNYALİ (Kritik: HTML'deki isimle aynı olmalı)
@socketio.on('execute_visual')
def handle_visual(data):
    # Remote'dan gelen veriyi (manage_slot veya lion_trigger) olduğu gibi Host'a basar
    emit('execute_visual', data, broadcast=True)

# 2. DÜZENLEME (EDIT MOVE) SİNYALİ
@socketio.on('toggle_edit')
def handle_edit(data):
    emit('toggle_edit', data, broadcast=True)

# Hata ayıklama için terminale yazdırır
@socketio.on('connect')
def test_connect():
    print(">>> Bir cihaz sisteme bağlandı!")

if __name__ == '__main__':
    # Render veya yerel çalıştırma için port ayarı
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, host='0.0.0.0', port=port)