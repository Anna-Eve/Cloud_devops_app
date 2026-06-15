#envoie événements dans kafka

from kafka import KafkaProducer
import json
import time
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC  = os.getenv("KAFKA_TOPIC",  "app-events")

def creer_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

def envoyer_evenement(producer, type_event, message):
    event = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source":    "kafka-producer",
        "type":      type_event,
        "message":   message
    }
    producer.send(KAFKA_TOPIC, event)
    producer.flush()
    print(f"[PRODUCER] Événement envoyé : {event}")
    return event

if __name__ == "__main__":
    print(f"Connexion à Kafka sur {KAFKA_BROKER}...")
    producer = creer_producer()
    print("Connecté ! Envoi d'événements toutes les 3 secondes. (Ctrl+C pour arrêter)\n")

    evenements = [
        ("deploy",  "Déploiement de la version 1.0.0"),
        ("test",    "Tests automatiques réussis"),
        ("health",  "Application opérationnelle"),
        ("metric",  "CPU: 45%, Mémoire: 60%"),
        ("alert",   "Latence élevée détectée : 350ms"),
    ]

    i = 0
    while True:
        type_e, msg = evenements[i % len(evenements)]
        envoyer_evenement(producer, type_e, msg)
        i += 1
        time.sleep(3)

