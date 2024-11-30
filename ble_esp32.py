import os
import asyncio
from bleak import BleakClient, BleakScanner
import pyautogui
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
import screen_brightness_control as sbc

# BLE UUID'leri
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"

# Ses kontrolü için başlangıç ayarları
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

async def handle_command(command):
    """Gelen komutları işle ve gerekli aksiyonları gerçekleştir"""
    print(f"\n➡️ İşleniyor: '{command}' komutu")

    if command == "ses_ac":
        volume.SetMasterVolumeLevel(-0.0, None)  # Max ses
        print("🔊 Ses açıldı (Maksimum)")

    elif command == "ses_kapat":
        volume.SetMasterVolumeLevel(-65.25, None)  # Min ses
        print("🔇 Ses kapatıldı (Minimum)")

    elif command == "ekran_goruntusu":
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        screenshot_path = os.path.join(desktop_path, "screenshot.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        print(f"📸 Ekran görüntüsü kaydedildi: {screenshot_path}")

    elif command == "parlaklik_ac":
        sbc.set_brightness(100)
        print("🌟 Ekran parlaklığı artırıldı (100%)")

    elif command == "parlaklik_kapat":
        sbc.set_brightness(0)
        print("🌑 Ekran parlaklığı kapatıldı (0%)")

    else:
        print("⚠️ Bilinmeyen komut alındı.")

async def notification_handler(sender, data):
    """BLE üzerinden gelen verileri işle"""
    command = data.decode()
    print(f"\n📩 Alınan komut: {command}")
    await handle_command(command)

async def run_ble_client():
    """BLE istemcisini başlat ve ESP32'ye bağlan"""
    device = None

    while device is None:
        print("🔍 ESP32 aranıyor...")
        device = await BleakScanner.find_device_by_name("ESP32_Control")
        if device is None:
            print("⏳ ESP32 bulunamadı, tekrar deneniyor...")
            await asyncio.sleep(1)

    print(f"\n✅ ESP32 bulundu: {device.name}")
    
    async with BleakClient(device.address) as client:
        print(f"🔗 Bağlantı kuruldu: {device.address}")
        
        # Bildirim callback'ini ayarla
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        print("📡 BLE bildirimleri dinleniyor...")

        # Bağlantıyı sürdür
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("\n🔌 Bağlantı sonlandırıldı.")

if __name__ == "__main__":
    print("🚀 BLE İstemci başlatılıyor...")
    try:
        asyncio.run(run_ble_client())
    except KeyboardInterrupt:
        print("\n❌ Program durduruldu.")
