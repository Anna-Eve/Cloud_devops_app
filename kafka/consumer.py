#lit événements de kafka

from kafka import KafkaConsumer
import json
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC  = os.getenv("KAFKA_TOPIC",  "app-events")

# Couleurs terminal
COULEURS = {
    "deploy":  "\033[92m",  # vert
    "test":    "\033[94m",  # bleu
    "health":  "\033[96m",  # cyan
    "metric":  "\033[93m",  # jaune
    "alert":   "\033[91m",  # rouge
}
RESET = "\033[0m"

def afficher_event(event):
    couleur = COULEURS.get(event.get("type", ""), "\033[97m")
    print(f"{couleur}[{event['timestamp']}] [{event['type'].upper()}] {event['message']}{RESET}")

if __name__ == "__main__":
    print(f"Connexion à Kafka sur {KAFKA_BROKER}...")
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="devops-consumer-group"
    )
    print(f"En écoute sur le topic '{KAFKA_TOPIC}'...\n")

    for message in consumer:
        event = message.value
        afficher_event(event)
