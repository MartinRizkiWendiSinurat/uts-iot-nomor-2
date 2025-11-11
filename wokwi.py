import network
import time
import ujson
from umqtt.simple import MQTTClient
from random import uniform

# --- WiFi Configuration ---
SSID = "Wokwi-GUEST"
PASSWORD = ""

# --- MQTT Configuration ---
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/db_cuaca"

# --- Connect to WiFi ---
print("Menghubungkan ke WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    print(".", end="")
    time.sleep(0.5)

print("\n✅ WiFi Terhubung!")
print("IP Address:", wlan.ifconfig()[0])

# --- MQTT Setup ---
client = MQTTClient("ESP32_Cuaca", MQTT_BROKER, port=MQTT_PORT)
client.connect()
print("✅ Terhubung ke MQTT Broker!")

# --- Main Loop ---
while True:
    # Data dummy (bisa diganti nanti pakai sensor DHT, LDR, dll)
    suhu = round(uniform(25, 35), 2)
    humid = round(uniform(40, 90), 2)
    lux = round(uniform(100, 900), 2)

    data = {
        "suhu": suhu,
        "humid": humid,
        "lux": lux
    }

    payload = ujson.dumps(data)
    client.publish(MQTT_TOPIC, payload)

    print(f"📤 Data terkirim ke {MQTT_TOPIC}: {payload}")
    time.sleep(3)