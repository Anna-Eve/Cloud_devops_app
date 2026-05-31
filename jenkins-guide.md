# Lancer la partie Jenkins
## Prérequis
- Docker installé et lancé : sudo systemctl start docker
- Git

## Structure attendue du projet
```
projet/
├── jenkins/
│   ├── Dockerfile      
│   └── Jenkinsfile     
└── app/
    ├── Dockerfile      
    ├── app.py
    └── tests/
```

## Étapes
### 1. Construire l'image Jenkins custom
```bash
cd jenkins/
docker build -t jenkins-custom .
```
> Long la première fois (~5 min), il télécharge les plugins et Kafka.

### 2. Lancer Jenkins
```bash
docker run -d \
  --name jenkins \
  -p 8080:8080 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins-custom
```
> Le `-v /var/run/docker.sock` permet à Jenkins de piloter Docker sur la machine.

### 3. Ouvrir Jenkins
Aller sur -> **http://localhost:8080**
Login par défaut : `admin` / `admin`

### 4. Créer le pipeline
1. Cliquer **New Item**
2. Nom : `flask-api-pipeline`
3. Choisir **Pipeline** -> OK
4. Dans *Pipeline* -> *Definition* : choisir **Pipeline script from SCM**
5. SCM : **Git**, mettre l'URL du repo
6. Script Path : `jenkins/Jenkinsfile`
7. **Save**

### 5. Lancer le pipeline
Cliquer **Build Now** sur la page du pipeline.
Les 3 stages apparaissent : **Build -> Test -> Deploy**

## Sans les fichiers dans app

Si `app/` n'existe pas encore, le stage **Build** va échouer.  

## Sans Kafka 
Les événements Kafka sont ignorés avec un warning, le pipeline continue quand même.

## Arrêter Jenkins
```bash
docker stop jenkins
docker rm jenkins
```