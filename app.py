from flask import Flask, jsonify, render_template
import mysql.connector

# Inisialisasi Flask
app = Flask(__name__)

# --- Koneksi ke Database ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db_cuaca"
)

@app.route('/api', methods=['GET'])
def get_data():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tb_cuaca ORDER BY id DESC LIMIT 10")
    data = cursor.fetchall()

    if not data:
        return jsonify({"message": "Belum ada data"}), 404

    # Ambil list nilai dari setiap kolom
    suhu_list = [row['suhu'] for row in data]
    humid_list = [row['humid'] for row in data]
    lux_list = [row['lux'] for row in data]

    # Buat hasil JSON
    result = {
        "jumlah_data": len(data),
        "suhumax": max(suhu_list),
        "suhumin": min(suhu_list),
        "suhurata": round(sum(suhu_list) / len(suhu_list), 2),
        "humidmax": max(humid_list),
        "humidmin": min(humid_list),
        "humidrata": round(sum(humid_list) / len(humid_list), 2),
        "luxmax": max(lux_list),
        "luxmin": min(lux_list),
        "luxrata": round(sum(lux_list) / len(lux_list), 2),
        "data_terbaru": data
    }

    return jsonify(result)

@app.route('/')
def index():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tb_cuaca ORDER BY id DESC LIMIT 10")
    data = cursor.fetchall()
    
    # Hitung statistik untuk ditampilkan di dashboard
    if data:
        suhu_list = [row['suhu'] for row in data]
        humid_list = [row['humid'] for row in data]
        lux_list = [row['lux'] for row in data]
        
        stats = {
            "suhu_tertinggi": max(suhu_list),
            "kelembapan_tertinggi": max(humid_list),
            "kecerahan_tertinggi": max(lux_list)
        }
    else:
        stats = {
            "suhu_tertinggi": 0,
            "kelembapan_tertinggi": 0,
            "kecerahan_tertinggi": 0
        }
    
    return render_template('index.html', data=data, stats=stats)

if __name__ == '__main__':
    print("🚀 Flask berjalan di http://127.0.0.1:5000")
    app.run(debug=True)