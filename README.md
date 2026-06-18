# Cloud_devops_app

🔴 Armand — Monitoring + Docker Compose

docker-compose.yml → Orchestration de tous les services
README.md → Manuel d'utilisation
monitoring/prometheus.yml → Config Prometheus
monitoring/devops.json → Dashboard Grafana

rapport final : Chapitre 3 résultats + Chapitre 4 conclusion

🟢 Anna-Eve — Application Flask + Kafka

app/app.py → API Flask avec les 3 routes
app/requirements.txt → Dépendances Python
app/Dockerfile → Conteneurisation de l'app
app/tests/test_app.py → Tests automatiques
kafka/producer.py → Envoie les événements
kafka/consumer.py → Lit les événements
rapport final : Chapitre 2 Architecture + diagrammes

🔵 Laure — Pipeline CI/CD Jenkins

jenkins/Jenkinsfile → Définition du pipeline CI/CD
jenkins/Dockerfile → Jenkins customisé avec Docker

rapport final : Chapitre 1 Introduction + problématique


# Cloud DevOps App — Lancer le projet

## Prérequis
- Docker installé et lancé
- Git

---

## Lancer tout le projet

```bash
# 1. Cloner le repo
git clone https://github.com/Anna-Eve/Cloud_devops_app
cd Cloud_devops_app

# 2. Lancer tous les services
docker-compose up -d
```

> ⏳ La première fois c'est long (~3-5 min), il télécharge toutes les images.

---

## Vérifier que tout tourne

```bash
docker ps
```

Tu dois voir ces conteneurs : `jenkins`, `flask-app`, `kafka`, `zookeeper`, `prometheus`, `grafana`, `node-exporter`

---

## Accéder aux services

| Service    | URL                        | Login              |
|------------|----------------------------|--------------------|
| Jenkins    | http://localhost:8080      | aucun (auto-login) |
| App Flask  | http://localhost:5000      | —                  |
| Grafana    | http://localhost:3000      | admin / admin123   |
| Prometheus | http://localhost:9090      | —                  |

---

## Lancer le pipeline CI/CD

1. Aller sur **http://localhost:8080**
2. Cliquer sur le pipeline `flask-api-pipeline`
3. Cliquer **Build Now**
4. Suivre l'exécution dans **Console Output**

Le pipeline exécute automatiquement :
- **Build** → construction de l'image Docker de l'app
- **Test** → 8 tests automatiques avec pytest
- **Deploy** → redémarrage du conteneur Flask

---

## Arrêter le projet

```bash
docker-compose down
```

## Relancer après un arrêt

```bash
docker-compose up -d
```

---

## Recréer le pipeline Jenkins (si disparu)

1. Aller sur **http://localhost:8080**
2. Cliquer **Nouveau Item**
3. Nom : `flask-api-pipeline`
4. Choisir **Pipeline** → OK
5. Dans la section *Pipeline* :
   - Definition : **Pipeline script from SCM**
   - SCM : **Git**
   - Repository URL : `https://github.com/Anna-Eve/Cloud_devops_app`
   - Branch : `*/main`
   - Script Path : `jenkins/Jenkinsfile`
6. Cliquer **Save**
7. Cliquer **Build Now**

> Le pipeline disparaît si le volume Jenkins est supprimé (ex: `docker-compose down -v`).
> Un simple `docker-compose down` sans `-v` le conserve.

---

## En cas de problème

**Jenkins ne démarre pas :**
```bash
docker-compose down
docker-compose up -d
```

**Le pipeline échoue au Build :**
Vérifier que Docker est bien lancé :
```bash
sudo systemctl start docker
```

**Les conteneurs ne sont plus là :**
```bash
docker-compose up -d
```