# ─────────────────────────────────────────────────────────────
# Jenkins custom — image pour le projet DevOps
#
# Ajouts par rapport à l'image officielle :
#   - Docker CLI  → pour builder/lancer des conteneurs depuis le pipeline
#   - Python 3    → pour exécuter les tests pytest directement si besoin
#   - kafka-clients (CLI) → pour que sendKafkaEvent() du Jenkinsfile fonctionne
# ─────────────────────────────────────────────────────────────
FROM jenkins/jenkins:lts-jdk17

USER root

# 1. Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        python3 \
        python3-pip \
        default-jre \
    && rm -rf /var/lib/apt/lists/*

# 2. Docker CLI (pour piloter le Docker host depuis Jenkins)
RUN curl -fsSL https://download.docker.com/linux/debian/gpg \
        | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) \
        signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
        https://download.docker.com/linux/debian \
        $(lsb_release -cs) stable" \
        > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# 3. Kafka CLI tools
# On télécharge la distribution binaire Kafka pour avoir
# kafka-console-producer.sh disponible dans le PATH
ENV KAFKA_VERSION=3.9.2
ENV SCALA_VERSION=2.13

RUN curl -fsSL \
        "https://downloads.apache.org/kafka/${KAFKA_VERSION}/kafka_${SCALA_VERSION}-${KAFKA_VERSION}.tgz" \
        -o /tmp/kafka.tgz \
    && tar -xzf /tmp/kafka.tgz -C /opt \
    && mv /opt/kafka_${SCALA_VERSION}-${KAFKA_VERSION} /opt/kafka \
    && rm /tmp/kafka.tgz

# Raccourci : kafka-console-producer.sh accessible sans chemin absolu
RUN ln -s /opt/kafka/bin/kafka-console-producer.sh /usr/local/bin/kafka-console-producer.sh \
    && ln -s /opt/kafka/bin/kafka-console-consumer.sh /usr/local/bin/kafka-console-consumer.sh

# 4. Plugins Jenkins (installés au build, pas au runtime)
# Utilise jenkins-plugin-cli fourni dans l'image de base
RUN jenkins-plugin-cli --plugins \
        git \
        workflow-aggregator \
        docker-workflow \
        junit \
        blueocean \
        github

# 5. Repasse en user jenkins (bonne pratique sécurité)
USER jenkins

# 6. Désactive le wizard de setup
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"

# Port standard Jenkins
EXPOSE 8080
EXPOSE 50000