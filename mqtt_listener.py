import json
import mysql.connector
import paho.mqtt.client as mqtt

# --- Koneksi ke database ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db_cuaca"
)
cursor = db.cursor()

# --- Callback saat pesan diterima ---
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        suhu = payload['suhu']
        humid = payload['humid']
        lux = payload['lux']

        sql = "INSERT INTO tb_cuaca (suhu, humid, lux) VALUES (%s, %s, %s)"
        cursor.execute(sql, (suhu, humid, lux))
        db.commit()
        print(f"✅ Data disimpan: Suhu={suhu}, Humid={humid}, Lux={lux}")

    except Exception as e:
        print("❌ Error:", e)

# --- Setup MQTT ---
client = mqtt.Client()
client.on_message = on_message
client.connect("test.mosquitto.org", 1883, 60)
client.subscribe("iot/db_cuaca")

print("🚀 Mendengarkan data dari MQTT broker...")
client.loop_forever()
