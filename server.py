import eventlet
eventlet.monkey_patch(all=True)

import os
from flask import Flask, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 🔥 KRİTİK AYARLAR: 
# 1. max_decode_packets_size: Resim verilerinin geçmesi için limiti 10MB yaptık.
# 2. ping_timeout: Bağlantının kopmaması için süreyi uzattık.
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    max_decode_packets_size=10000000,
    ping_timeout=60
)

# Koltukları hafızada tutmak için liste (Sunucu kapanana kadar veriler gitmez)
seats_state = [None] * 8

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

# Yeni Remote ve Host ile tam uyumlu sinyal: seatUpdate
@socketio.on('seatUpdate')
def handle_seat_update(data):
    seat_index = data.get('seatIndex')
    if seat_index is not None:
        seats_state[seat_index] = data.get('userData')
        print(f"--> Koltuk Güncellendi: {seat_index}")
        emit('seatUpdate', data, broadcast=True)

# Koltuk boşaltma sinyali
@socketio.on('seatClear')
def handle_seat_clear(data):
    seat_index = data.get('seatIndex')
    if seat_index is not None:
        seats_state[seat_index] = None
        print(f"--> Koltuk Boşaltıldı: {seat_index}")
        emit('seatClear', data, broadcast=True)

# Hediye sinyali
@socketio.on('giftReceived')
def handle_gift(data):
    print(f"--> Hediye Geldi: {data.get('giftType')}")
    emit('giftReceived', data, broadcast=True)

# Bağlanan yeni cihazlara mevcut koltuk durumunu gönderir
@socketio.on('register')
def handle_register(data):
    emit('fullSync', {'seats': seats_state})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)