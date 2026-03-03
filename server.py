import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Dosyaları internetten sunabilmek için gerekli
@app.route('/')
def index(): return send_from_directory('.', 'Host.html')

@app.route('/remote')
def remote(): return send_from_directory('.', 'Remote.html')

@app.route('/<path:path>')
def static_files(path): return send_from_directory('.', path)

@socketio.on('manage_slot')
def handle_slot(data):
    emit('update_host', data, broadcast=True)

@socketio.on('trigger_lion')
def handle_lion():
    emit('lion_trigger', broadcast=True)

if __name__ == '__main__':
    # Render'ın verdiği portu otomatik yakalar
    port = int(os.environ.get("PORT", 5001))
    socketio.run(app, host='0.0.0.0', port=port)