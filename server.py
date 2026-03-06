import eventlet
# Render üzerindeki kilitlenme (RLock) hatalarını bitirmek için şart
eventlet.monkey_patch(all=True)

import os
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from TikTokLive import TikTokLiveClient
from TikTokLive.events import GiftEvent

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)

# Bağlantı kopmalarını önlemek için optimize edilmiş soket ayarları
socketio = SocketIO(app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25)

# Senin TikTok kullanıcı adın
client = TikTokLiveClient(unique_id="@mylevelupo")

@socketio.on('execute_visual')
def handle_visual(data):
    """
    Bu fonksiyon senin Remote panelinden gönderdiğin komutları işler.
    Kullanıcı adını yazarsın, o Nick ve Profil Resmini TikTok'tan çeker.
    """
    if data.get('action') == 'manage_slot' and data.get('username'):
        try:
            # TikTok üzerinden kullanıcının takma adını ve resmini sorguluyoruz
            user = client.fetch_user_info(data['username']) 
            
            data['name'] = user.nickname  # Ekranda görünecek süslü isim
            data['avatar'] = user.avatar_thumb.url_list[0] # Profil resmi URL'si
            print(f"Kullanıcı Bulundu: {user.nickname}")
        except Exception as e:
            print(f"TikTok Bilgi Çekme Hatası: {e}")
            # Eğer kullanıcı bulunamazsa yazdığın ismi nickname olarak kullanır
            data['name'] = data['username']
            data['avatar'] = "https://www.gravatar.com/avatar/0?d=mp"

    # Hazırlanan veriyi tüm ekranlara (Host.html) gönderir
    emit('execute_visual', data, broadcast=True)

# TikTok hediye dinleyicisi arka planda sadece bilgi amaçlı çalışır
@client.on(GiftEvent)
async def on_gift(event: GiftEvent):
    socketio.emit('tiktok_gift_alert', {
        'user': event.user.unique_id,
        'gift_name': event.gift.name,
        'diamonds': event.gift.diamond_count
    })

def start_tiktok():
    try:
        client.run()
    except:
        pass

socketio.start_background_task(start_tiktok)

# Sayfa Yönlendirmeleri
@app.route('/')
def index(): return send_from_directory('.', 'Host.html')

@app.route('/remote')
def remote_page(): return send_from_directory('.', 'Remote.html')

@app.route('/<path:path>')
def static_files(path): return send_from_directory('.', path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)