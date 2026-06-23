# API Flask avec les 3 routes et tracking automatique des erreurs HTTP

from flask import Flask, request, jsonify
from kafka import KafkaProducer
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import json
import time
import logging
import os

# ─── Configuration ────────────────────────────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC  = os.getenv("KAFKA_TOPIC",  "app-events")

# ─── Métriques Prometheus ─────────────────────────────────────────────────────
# AJOUT du label "status_code" pour trier les succès et les erreurs dans Grafana
REQUEST_COUNT   = Counter("app_requests_total", "Nombre total de requêtes", ["method", "endpoint", "status_code"])
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Latence des requêtes")
EVENT_COUNT     = Counter("app_events_total", "Nombre d'événements envoyés à Kafka")

# ─── Connexion Kafka (optionnelle — ne plante pas si Kafka est absent) ─────────
def get_producer():
    try:
        return KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
    except Exception as e:
        logger.warning(f"Kafka non disponible : {e}")
        return None

# ─── Intercepteur de Métriques (Middleware) ───────────────────────────────────
@app.after_request
def log_request_metrics(response):
    if request.path != "/metrics":
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.path,
            status_code=str(response.status_code)
        ).inc()
        # Ajouter ceci — latence sur toutes les routes
        REQUEST_LATENCY.observe(time.time() - getattr(request, '_start_time', time.time()))
    return response

@app.before_request
def start_timer():
    request._start_time = time.time()

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Route principale — vérifie que l'app tourne."""
    return jsonify({
        "status":  "ok",
        "message": "Plateforme DevOps — Application Flask opérationnelle",
        "version": "1.0.0"
    })


@app.route("/health")
def health():
    """Route de santé — utilisée par Jenkins et Prometheus."""
    return jsonify({
        "status":    "healthy",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })


@app.route("/event", methods=["POST"])
def send_event():
    """Reçoit un événement JSON et l'envoie dans Kafka."""
    start = time.time()

    # Flask lève une erreur 415 automatique si ce n'est pas du JSON, l'intercepteur la verra
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corps JSON requis"}), 400

    event = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source":    "flask-app",
        "data":      data
    }

    producer = get_producer()
    if producer:
        producer.send(KAFKA_TOPIC, event)
        producer.flush()
        EVENT_COUNT.inc()
        logger.info(f"Événement envoyé dans Kafka : {event}")
        status = "sent_to_kafka"
    else:
        logger.warning("Kafka indisponible — événement non envoyé")
        status = "kafka_unavailable"

    REQUEST_LATENCY.observe(time.time() - start)
    return jsonify({"status": status, "event": event}), 201


@app.route("/metrics")
def metrics():
    """Expose les métriques pour Prometheus."""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


# ─── Démarrage ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)