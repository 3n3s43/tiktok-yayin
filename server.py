import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)

# Gunicorn + Eventlet ikilisi için en stabil ayar budur
socketio = SocketIO(app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    logger=True, 
    engineio_logger=True)

@app.route('/')
def index(): 
    return send_from_directory('.', 'Host.html')

@app.route('/remote')
def remote_page(): 
    return send_from_directory('.', 'Remote.html')

@app.route('/<path:path>')
def static_files(path): 
    return send_from_directory('.', path)

@socketio.on('execute_visual')
def handle_visual(data):
    emit('execute_visual', data, broadcast=True)

@socketio.on('toggle_edit')
def handle_edit(data):
    emit('toggle_edit', data, broadcast=True)

if __name__ == '__main__':
    # Render/Orender için portu dışarıdan alıyoruz
    port = int(os.environ.get("PORT", 10000))
    # Gunicorn kullanırken bu kısım aslında devre dışı kalır ama 
    # yerelde test için durması iyidir.
    socketio.run(app, host='0.0.0.0', port=port)