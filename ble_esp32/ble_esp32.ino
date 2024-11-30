#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// Dokunmatik pinler
#define TOUCH_PIN_1 33  // GPIO 33 (P33)
#define TOUCH_PIN_2 14  // GPIO 14 (P14)
#define TOUCH_PIN_3 13  // GPIO 13 (P13)
#define TOUCH_PIN_4 15  // GPIO 15 (P15)
#define TOUCH_PIN_5 32  // GPIO 32 (P32)

#define TOUCH_THRESHOLD 40  // Dokunma algılama eşiği

BLEServer *pServer = NULL;
BLECharacteristic *pCharacteristic = NULL;
BLEAdvertising *pAdvertising = NULL;
bool deviceConnected = false;
int connectedDevices = 0;

// Pin durumlarını takip için
int lastTouchedPin = -1;
unsigned long lastTouchTime = 0;

// Pinlere atanacak komutlar
const char* commands[] = {
    "ses_ac",           // Pin 1
    "ses_kapat",        // Pin 2
    "parlaklik_ac",     // Pin 3
    "parlaklik_kapat",  // Pin 4
    "ekran_goruntusu"   // Pin 5
};

// BLE sunucu callback sınıfı
class MyServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
        connectedDevices++;
        Serial.print("Connected devices: ");
        Serial.println(connectedDevices);
        if (connectedDevices < 2) {
            delay(100);
            pAdvertising->start();
        }
    };

    void onDisconnect(BLEServer* pServer) {
        connectedDevices--;
        Serial.print("Connected devices: ");
        Serial.println(connectedDevices);
        delay(100);
        pAdvertising->start();
    }
};

// BLE karakteristik callback sınıfı
class MyCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
        String rxValue = pCharacteristic->getValue();
        if (rxValue.length() > 0) {
            Serial.println("Received value:");
            for (int i = 0; i < rxValue.length(); i++) {
                Serial.print(rxValue[i]);
            }
            Serial.println();
            pCharacteristic->setValue(rxValue.c_str());
            pCharacteristic->notify();
        }
    }
};

void setup() {
    Serial.begin(115200);

    // BLE cihazı başlat
    BLEDevice::init("ESP32_Control");
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

    BLEService *pService = pServer->createService(SERVICE_UUID);
    pCharacteristic = pService->createCharacteristic(
                        CHARACTERISTIC_UUID,
                        BLECharacteristic::PROPERTY_READ   |
                        BLECharacteristic::PROPERTY_WRITE  |
                        BLECharacteristic::PROPERTY_NOTIFY
                      );
    pCharacteristic->setCallbacks(new MyCallbacks());
    pCharacteristic->addDescriptor(new BLE2902());
    pService->start();

    pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->start();

    Serial.println("BLE server ready!");
}

void loop() {
    int currentPin = -1;

    // Pinlerin dokunma durumunu kontrol et
    if (touchRead(TOUCH_PIN_1) < TOUCH_THRESHOLD) currentPin = 1;
    else if (touchRead(TOUCH_PIN_2) < TOUCH_THRESHOLD) currentPin = 2;
    else if (touchRead(TOUCH_PIN_3) < TOUCH_THRESHOLD) currentPin = 3;
    else if (touchRead(TOUCH_PIN_4) < TOUCH_THRESHOLD) currentPin = 4;
    else if (touchRead(TOUCH_PIN_5) < TOUCH_THRESHOLD) currentPin = 5;

    // Eğer bir pin dokunulduysa
    if (currentPin != -1) {
        if (lastTouchedPin != currentPin) {
            // Yeni bir dokunma algılandı
            Serial.print("Pin ");
            Serial.print(currentPin);
            Serial.println(" basıldı.");
            lastTouchedPin = currentPin;
            lastTouchTime = millis();

            // BLE üzerinden mesaj gönder
            pCharacteristic->setValue(commands[currentPin - 1]);  // Komut atanır
            pCharacteristic->notify();
        }
    } else if (lastTouchedPin != -1) {
        // Dokunma bırakıldıysa
        if (millis() - lastTouchTime > 50) {
            Serial.print("Pin ");
            Serial.print(lastTouchedPin);
            Serial.println(" bırakıldı.");

            // BLE üzerinden bırakılma mesajı gönder
            String releaseMessage = String(commands[lastTouchedPin - 1]) + "_birakildi";
            pCharacteristic->setValue(releaseMessage.c_str());
            pCharacteristic->notify();

            lastTouchedPin = -1;  // Durumu sıfırla
        }
    }

    delay(50);  // Gürültüyü önlemek için kısa bir bekleme
}
