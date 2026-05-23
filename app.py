from flask import Flask, jsonify, request
from flask_cors import CORS
from collections import deque
from datetime import datetime, timezone
import threading

app = Flask(__name__)

CORS(app)

lock = threading.Lock()

sensor_actual = {
    "dist": -1,
    "nivel": "sin_senal",
    "alerta": False,
    "timestamp": None,
}

alertas_historial = deque(maxlen=50)


def ahora_iso():
    return datetime.now(timezone.utc).isoformat()

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "message": "API de Nano-Guardian funcionando",
        "endpoints": [
            "GET  /api/sensor/ultima       → última lectura del HC-SR04",
            "POST /api/sensor              → ESP32 publica lectura",
            "GET  /api/alertas/ultima      → última alerta crítica",
            "GET  /api/alertas/historial   → últimas 50 alertas",
            "POST /api/alertas             → ESP32 publica alerta",
        ],
    })

@app.route("/api/sensor", methods=["POST"])
def post_sensor():
    """
    El ESP32 llama aquí ~2 veces por segundo con:
        {"dist": 42, "nivel": "peligro", "alerta": true}
    Guardamos la última lectura en memoria; cualquiera puede consultarla
    via GET /api/sensor/ultima.
    """
    data = request.get_json(silent=True) or {}

    try:
        dist = int(data.get("dist", -1))
    except (TypeError, ValueError):
        dist = -1

    nivel = str(data.get("nivel", "sin_senal"))
    alerta = bool(data.get("alerta", False))

    with lock:
        sensor_actual.update({
            "dist": dist,
            "nivel": nivel,
            "alerta": alerta,
            "timestamp": ahora_iso(),
        })

    return jsonify({"ok": True}), 201


@app.route("/api/sensor/ultima", methods=["GET"])
def get_sensor_ultima():
    """Devuelve la última lectura — la app MAUI hace polling aquí."""
    with lock:
        return jsonify(sensor_actual), 200

@app.route("/sensor", methods=["GET"])
def get_sensor_legacy():
    return get_sensor_ultima()

@app.route("/api/alertas", methods=["POST"])
def post_alerta():
    """
    El ESP32 llama aquí SOLO cuando detecta nivel "critico" (≤30 cm)
    o una caída (con un MPU-6050 futuro). Esquema:
        {
          "paciente": "Nehemías",
          "fuerza_impacto_g": 5.2,
          "estado": "Caída detectada"
        }
    """
    data = request.get_json(silent=True) or {}

    alerta = {
        "paciente": str(data.get("paciente", "Desconocido")),
        "fuerza_impacto_g": float(data.get("fuerza_impacto_g", 0)),
        "estado": str(data.get("estado", "Alerta sin descripción")),
        "timestamp": ahora_iso(),
    }

    with lock:
        alertas_historial.append(alerta)

    return jsonify({"ok": True, "alerta": alerta}), 201


@app.route("/api/alertas/ultima", methods=["GET"])
def get_alerta_ultima():
    """
    Devuelve la última alerta registrada. Si no hay ninguna todavía,
    devolvemos un placeholder semánticamente coherente.
    """
    with lock:
        if alertas_historial:
            return jsonify(alertas_historial[-1]), 200
        return jsonify({
            "paciente": "—",
            "fuerza_impacto_g": 0,
            "estado": "Sin alertas registradas todavía",
            "timestamp": None,
        }), 200


@app.route("/api/alertas/historial", methods=["GET"])
def get_alertas_historial():
    """Devuelve las últimas N alertas (más reciente primero)."""
    with lock:
        return jsonify(list(reversed(alertas_historial))), 200

if __name__ == "__main__":
    # En Render/Proxmox se usa gunicorn → este bloque no se ejecuta.
    app.run(host="0.0.0.0", port=5000, debug=True)
