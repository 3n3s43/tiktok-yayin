import eventlet
eventlet.monkey_patch() # Hataları önlemek için en üstte olmalı

import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)

# Gunicorn + Eventlet ikilisi için en stabil ayar
socketio = SocketIO(app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    logger=True, 
    engineio_logger=True)

# --- TİKTOK BAĞLANTISI ---
# Kullanıcı adınla yayını dinlemeye başlar
client = TikTokLiveClient(unique_id="@mylevelupo")

@client.on("gift")
async def on_gift(event: GiftEvent):
    # TikTok'tan gelen hediyeyi Remote ekranına bildirim olarak gönderir
    socketio.emit('tiktok_gift_alert', {
        'user': event.user.unique_id,
        'gift_name': event.gift.name,
        'diamonds': event.gift.diamond_count
    })
    print(f"Hediye Alındı: {event.gift.name} - Gönderen: {event.user.unique_id}")

# TikTok dinleyicisini arka planda güvenli çalıştırma fonksiyonu
def start_tiktok():
    try:
        print("TikTok Canlı Yayın Bağlantısı Başlatılıyor...")
        client.run()
    except Exception as e:
        print(f"TikTok Bağlantı Hatası: {e}")

# Sunucu ayağa kalktığında TikTok dinleyicisini arka planda başlat
socketio.start_background_task(start_tiktok)

# --- YOLLAR (ROUTES) ---
@app.route('/')
def index(): 
    return send_from_directory('.', 'Host.html')

@app.route('/remote')
def remote_page(): 
    return send_from_directory('.', 'Remote.html')

@app.route('/<path:path>')
def static_files(path): 
    return send_from_directory('.', path)

# --- SOKET OLAYLARI (Remote ve Host Arasındaki İletişim) ---
@socketio.on('execute_visual')
def handle_visual(data):
    # Remote'dan gelen komutu tüm bağlı ekranlara (Host) yayar
    emit('execute_visual', data, broadcast=True)

@socketio.on('toggle_edit')
def handle_edit(data):
    emit('toggle_edit', data, broadcast=True)

if