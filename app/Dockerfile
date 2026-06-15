# ── Image de base ──────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ── Dossier de travail ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Dépendances (couche cachée séparément pour les rebuilds rapides) ───────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Code source ────────────────────────────────────────────────────────────────
COPY . .

# ── Port exposé ────────────────────────────────────────────────────────────────
EXPOSE 5000

# ── Démarrage ──────────────────────────────────────────────────────────────────
CMD ["python", "app.py"]
