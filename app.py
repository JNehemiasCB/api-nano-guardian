from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "message": "API de Nano-Guardian funcionando"
    })

@app.route('/sensor', methods=['GET'])
def get_sensor_data():
    # Simulamos datos del ESP32/Arduino
    # En la vida real, aquí leerías una base de datos o un broker MQTT
    datos = {
        "distancia": round(random.uniform(10.5, 200.0), 2),
        "alerta": random.choice([True, False]),
        "unidad": "cm"
    }
    return jsonify(datos)

if __name__ == '__main__':
    app.run(debug=True)