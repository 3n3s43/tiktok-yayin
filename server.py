import os, requests
from flask import Flask, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# TikTok profil resmi çekme (Simüle edilmiş - Gerçek API için kütüphane gerekir)
@app.route('/get_tiktok/<handle>')
def get_tiktok(handle):
    # Bu kısım normalde bir API'den çeker, şimdilik temsili bir resim dönüyoruz
    avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={handle}"
    return jsonify({"name": handle, "avatar": avatar_url})

@app.route('/')
def index(): return send_from_directory('.', 'Host.html')

@app.route('/remote')
def remote_page(): return send_from_directory('.', 'Remote.html')

@app.route('/<path:path>')
def static_files(path): return send_from_directory('.', path)

@socketio.on('manage_slot')
def handle_slot(data): emit('update_host', data, broadcast=True)

@socketio.on('toggle_edit')
def handle_edit(data): emit('toggle_edit', data, broadcast=True)

@socketio.on('trigger_lion')
def handle_lion(data=None): emit('lion_trigger', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get("PORT", 5001)))