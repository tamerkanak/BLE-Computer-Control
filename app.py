import os
import asyncio
import threading
from bleak import BleakClient, BleakScanner
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import screen_brightness_control as sbc
from flask import Flask, request, jsonify, render_template
import librosa
import numpy as np
import joblib

# Flask uygulaması
app = Flask(__name__)

# BLE UUID'leri
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

# Ses kontrolü için başlangıç ayarları
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Model dosyaları
UPLOAD_FOLDER = 'uploaded_audios'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Klasör yoksa oluştur

lr_model = joblib.load('lr_model.joblib')
scaler = joblib.load('scaler.joblib')

# BLE ve Model logları için global liste
logs = []

def log_message(message):
    """Log mesajını kaydet ve terminale yazdır"""
    logs.append(message)
    print(message)

@app.route('/logs')
def get_logs():
    """Logları döndüren API"""
    return jsonify(logs)


@app.route('/')
def index():
    """Anasayfa: Logları göster"""
    return render_template('index.html', logs=logs)

def extract_features(audio_path):
    """Ses dosyasından özellik çıkarma"""
    audio, sr = librosa.load(audio_path, duration=1.5)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
    mel = librosa.feature.melspectrogram(y=audio, sr=sr)
    mfccs_mean = np.mean(mfccs.T, axis=0)
    mfccs_std = np.std(mfccs.T, axis=0)
    chroma_mean = np.mean(chroma.T, axis=0)
    mel_mean = np.mean(mel.T, axis=0)
    features = np.concatenate([mfccs_mean, mfccs_std, chroma_mean, mel_mean])
    return features

@app.route('/predict', methods=['POST'])
def predict():
    """Ses dosyasını al, kaydet ve tahmin yap"""
    if 'file' not in request.files:
        log_message("❌ Hata: Dosya bulunamadı.")
        return jsonify({'error': 'No file part'}), 400
    
    audio_file = request.files['file']
    if audio_file.filename == '':
        log_message("❌ Hata: Seçili dosya yok.")
        return jsonify({'error': 'No selected file'}), 400
    
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)
    
    try:
        features = extract_features(file_path)
        features_scaled = scaler.transform(features.reshape(1, -1))
        prediction = lr_model.predict(features_scaled)[0]
        log_message(f"✅ Tahmin tamamlandı: {prediction}")
    except Exception as e:
        log_message(f"❌ Tahmin sırasında hata: {e}")
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'prediction': prediction})

async def handle_command(command):
    """Gelen BLE komutlarını işle"""
    log_message(f"➡️ İşleniyor: '{command}' komutu")

    if command == "ses_ac":
        volume.SetMasterVolumeLevel(-0.0, None)
        log_message("🔊 Ses açıldı (Maksimum)")
    elif command == "ses_kapat":
        volume.SetMasterVolumeLevel(-65.25, None)
        log_message("🔇 Ses kapatıldı (Minimum)")
    elif command == "ekran_goruntusu":
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        screenshot_path = os.path.join(desktop_path, "screenshot.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        log_message(f"📸 Ekran görüntüsü kaydedildi: {screenshot_path}")
    elif command == "parlaklik_ac":
        sbc.set_brightness(100)
        log_message("🌟 Ekran parlaklığı artırıldı (100%)")
    elif command == "parlaklik_kapat":
        sbc.set_brightness(0)
        log_message("🌑 Ekran parlaklığı kapatıldı (0%)")
    else:
        log_message("⚠️ Bilinmeyen komut alındı.")

async def notification_handler(sender, data):
    """BLE üzerinden gelen verileri işle"""
    command = data.decode()
    log_message(f"📩 Alınan komut: {command}")
    await handle_command(command)

async def run_ble_client():
    """BLE istemcisini başlat"""
    device = None
    while device is None:
        log_message("🔍 ESP32 aranıyor...")
        device = await BleakScanner.find_device_by_name("ESP32_Control")
        if device is None:
            log_message("⏳ ESP32 bulunamadı, tekrar deneniyor...")
            await asyncio.sleep(1)

    log_message(f"\n✅ ESP32 bulundu: {device.name}")
    async with BleakClient(device.address) as client:
        log_message(f"🔗 Bağlantı kuruldu: {device.address}")
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        log_message("📡 BLE bildirimleri dinleniyor...")
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            log_message("🔌 Bağlantı sonlandırıldı.")
@app.route('/command', methods=['POST'])
def handle_manual_command():
    """Web arayüzünden gelen komutları işle"""
    try:
        data = request.json
        command = data.get('command')
        
        if not command:
            return jsonify({'error': 'Komut bulunamadı'}), 400
            
        # Komut için asenkron işleyiciyi çağır
        asyncio.run(handle_command(command))
        return jsonify({'success': True})
    except Exception as e:
        log_message(f"❌ Komut işlenirken hata oluştu: {str(e)}")
        return jsonify({'error': str(e)}), 500
def start_ble_loop():
    """BLE döngüsünü başlat"""
    asyncio.run(run_ble_client())

if __name__ == '__main__':
    # BLE döngüsünü ayrı bir thread'de başlat
    ble_thread = threading.Thread(target=start_ble_loop, daemon=True)
    ble_thread.start()

    # Flask uygulamasını başlat
    app.run(host='0.0.0.0', port=5000)
