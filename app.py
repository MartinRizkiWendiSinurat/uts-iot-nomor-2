from flask import Flask, render_template, jsonify, request
import mysql.connector
import paho.mqtt.publish as publish
import json

app = Flask(__name__)

# === KONFIGURASI DATABASE ===
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_hidroponik"
    )

# === KONFIGURASI MQTT ===
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC_CONTROL = "iot/hidroponik/control"

# === HALAMAN UTAMA ===
@app.route("/")
def index():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM data_sensor ORDER BY id DESC LIMIT 10")
        data = cursor.fetchall()
        cursor.close()
        db.close()

        latest = data[0] if data else None
        return render_template("index.html", data=data, latest=latest)
    except Exception as e:
        return f"<h3>❌ Gagal memuat data: {e}</h3>"

# === API: AMBIL DATA REALTIME ===
@app.route("/api/realtime")
def api_realtime():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM data_sensor ORDER BY id DESC LIMIT 1")
        data = cursor.fetchone()
        cursor.close()
        db.close()
        if data:
            return jsonify({"status": "success", "data": data})
        else:
            return jsonify({"status": "error", "message": "Belum ada data"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# === API: KONTROL POMPA ===
@app.route("/api/control/pompa", methods=["POST"])
def control_pompa():
    try:
        req = request.get_json()
        status_pompa = req.get("pompa", False)

        # payload JSON untuk dikirim ke ESP32 via MQTT
        payload = json.dumps({"pompa": status_pompa})
        publish.single(
            MQTT_TOPIC_CONTROL,
            payload,
            hostname=MQTT_BROKER,
            port=MQTT_PORT,
        )

        return jsonify({
            "status": "success",
            "message": f"Pompa {'dinyalakan' if status_pompa else 'dimatikan'}"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    print("🚀 Flask Dashboard Hidroponik IoT Aktif")
    print("👉 Buka di browser: http://127.0.0.1:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)
