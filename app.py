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


# ─────────────────────────────────────────────────────────────────────
# NUEVO ENDPOINT — requerido por la HU "Consumo de la API"
# La app MAUI llama GET /api/alertas/ultima y pinta los datos en la
# pantalla Dashboard.  Por ahora simulamos la "última alerta"; cuando
# tengas BD o un POST desde el ESP32, reemplaza el dict por la lectura
# real (la app móvil NO necesita cambiar).
# ─────────────────────────────────────────────────────────────────────
@app.route('/api/alertas/ultima', methods=['GET'])
def obtener_ultima_alerta():
    alerta = {
        "paciente": "Juan Pérez (Real)",
        "fuerza_impacto_g": 5,
        "estado": "¡Caída Detectada en API!"
    }
    return jsonify(alerta), 200


if __name__ == '__main__':
    app.run(debug=True)
