import json
import mysql.connector
import paho.mqtt.client as mqtt
from datetime import datetime

# === KONEKSI KE DATABASE ===
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db_hidroponik"
)
cursor = db.cursor()

# === BUAT TABEL JIKA BELUM ADA ===
cursor.execute("""
CREATE TABLE IF NOT EXISTS data_sensor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    suhu FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    lux INT NOT NULL,
    status VARCHAR(20),
    pompa BOOLEAN,
    buzzer BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
db.commit()
print("✅ Database siap!\n")

# === CALLBACK SAAT TERHUBUNG ===
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("✅ Terhubung ke MQTT Broker!")
        client.subscribe("iot/hidroponik/sensor")
        print("📥 Subscribe ke topic: iot/hidroponik/sensor")
        print("🎧 Mendengarkan data...\n")
    else:
        print(f"❌ Gagal terhubung, reason code: {reason_code}")

# === CALLBACK SAAT PESAN DITERIMA ===
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        suhu = float(payload.get('suhu', 0))
        humidity = float(payload.get('humidity', 0))
        lux = int(payload.get('lux', 0))
        status = str(payload.get('status', 'UNKNOWN'))
        pompa = bool(payload.get('pompa', 0))
        buzzer = bool(payload.get('buzzer', 0))

        sql = """INSERT INTO data_sensor 
                 (suhu, humidity, lux, status, pompa, buzzer) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (suhu, humidity, lux, status, pompa, buzzer))
        db.commit()

        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ [{waktu}] Data disimpan:")
        print(f"   Suhu={suhu}°C, Humidity={humidity}%, Lux={lux}")
        print(f"   Status={status}, Pompa={'ON' if pompa else 'OFF'}\n")

    except json.JSONDecodeError:
        print("❌ Error: Format JSON tidak valid")
    except mysql.connector.Error as e:
        print(f"❌ Error Database: {e}")
        db.rollback()
    except Exception as e:
        print(f"❌ Error: {e}")

# === SETUP MQTT CLIENT (PAHO 2.x) ===
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="MQTT_Listener_Hidroponik"
)

client.on_connect = on_connect
client.on_message = on_message

# === KONEKSI KE BROKER ===
try:
    print("🔌 Menghubungkan ke MQTT Broker...")
    client.connect("test.mosquitto.org", 1883, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("\n⏹  Program dihentikan oleh user")
    cursor.close()
    db.close()
    client.disconnect()
except Exception as e:
    print(f"❌ Error: {e}")
    cursor.close()
    db.close()
