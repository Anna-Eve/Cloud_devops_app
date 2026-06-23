# --- Script de demo - Generation de trafic automatique ----------------------
# Lance ce script pendant la presentation pour avoir de vraies donnees dans Grafana
# Usage : .\demo.ps1
# Arret  : Ctrl+C

$BASE_URL = "http://localhost:5000"
$DUREE_MINUTES = 30   # duree totale du script
$DELAI_SECONDES = 2   # pause entre chaque rafale de requetes

# Couleurs
function Write-OK    { param($msg) Write-Host "[OK]  $msg" -ForegroundColor Green }
function Write-INFO  { param($msg) Write-Host "[-->] $msg" -ForegroundColor Cyan }
function Write-WARN  { param($msg) Write-Host "[!!]  $msg" -ForegroundColor Yellow }
function Write-TITLE { param($msg) Write-Host "`n$msg" -ForegroundColor Magenta }

# --- Verification que l'app tourne -------------------------------------------
Write-TITLE "======================================================"
Write-TITLE "   DEMO DevOps - Generation de trafic automatique"
Write-TITLE "======================================================"
Write-Host ""

try {
    $check = Invoke-RestMethod -Uri "$BASE_URL/health" -Method GET -TimeoutSec 3
    Write-OK "Flask App accessible → status: $($check.status)"
} catch {
    Write-WARN "Flask App inaccessible sur $BASE_URL"
    Write-WARN "Lance d'abord : docker compose up -d"
    exit 1
}

Write-Host ""
Write-INFO "Ouverture de Grafana dans le navigateur..."
Start-Process "http://localhost:3000/d/devops-main"
Start-Sleep -Seconds 2

Write-INFO "Generation de trafic pendant $DUREE_MINUTES minutes..."
Write-INFO "Appuie sur Ctrl+C pour arreter`n"

# --- evenements a envoyer dans Kafka via Flask -------------------------------
$EVENTS = @(
    @{ type="deploy";  message="Deploiement version 1.0.0 reussi";      service="flask-app" },
    @{ type="test";    message="Tests unitaires : 8/8 passes";           service="flask-app" },
    @{ type="health";  message="Health check OK - latence 12ms";         service="flask-app" },
    @{ type="metric";  message="CPU: 42%, RAM: 61%, Disk: 23%";          service="node-exporter" },
    @{ type="deploy";  message="Build Jenkins #42 - SUCCESS";            service="jenkins" },
    @{ type="alert";   message="Latence elevee detectee : 850ms";        service="flask-app" },
    @{ type="test";    message="Pipeline CI/CD complet en 47 secondes";  service="jenkins" },
    @{ type="metric";  message="Kafka consumer lag: 0 messages";         service="kafka" }
)

$compteur = 0
$debut = Get-Date
$fin = $debut.AddMinutes($DUREE_MINUTES)
$phase = 0

while ((Get-Date) -lt $fin) {
    $phase++
    $elapsed = [math]::Round(((Get-Date) - $debut).TotalMinutes, 1)
    Write-TITLE "--- Phase $phase - ${elapsed}min ecoulees -------------------"

    # 1. GET / (route principale)
    try {
        $r = Invoke-RestMethod -Uri "$BASE_URL/" -Method GET
        Write-OK "GET /  → $($r.status)"
        $compteur++
    } catch { Write-WARN "GET / echoue" }

    # 2. GET /health (x3 pour generer de la volumetrie)
    1..3 | ForEach-Object {
        try {
            $r = Invoke-RestMethod -Uri "$BASE_URL/health" -Method GET
            Write-OK "GET /health  → $($r.status)"
            $compteur++
        } catch { Write-WARN "GET /health echoue" }
        Start-Sleep -Milliseconds 300
    }

    # 3. POST /event avec un evenement aleatoire
    $event = $EVENTS[$phase % $EVENTS.Count]
    try {
        $body = $event | ConvertTo-Json
        $r = Invoke-RestMethod -Uri "$BASE_URL/event" -Method POST `
            -Body $body -ContentType "application/json"
        Write-OK "POST /event → [$($event.type.ToUpper())] $($event.message)"
        $compteur++
    } catch { Write-WARN "POST /event echoue" }

    # 4. Toutes les 5 phases : simuler un pic de trafic (pour rendre les graphes interessants)
    if ($phase % 5 -eq 0) {
        Write-INFO "- Simulation pic de trafic..."
        1..10 | ForEach-Object {
            try {
                Invoke-RestMethod -Uri "$BASE_URL/health" -Method GET | Out-Null
                $compteur++
            } catch {}
            Start-Sleep -Milliseconds 100
        }
        Write-OK "Pic genere - 10 requetes rapides"
    }

    # 5. Toutes les 8 phases : simuler une erreur (route inexistante → 404)
    if ($phase % 8 -eq 0) {
        Write-INFO "- Simulation erreur 404..."
        try {
            Invoke-WebRequest -Uri "$BASE_URL/route-inexistante" -Method GET | Out-Null
        } catch {
            Write-OK "Erreur 404 generee (normal - pour les graphes)"
            $compteur++
        }
    }

    # Resume
    Write-Host ""
    Write-INFO "Total requetes envoyees : $compteur"
    Write-INFO "Prochaine rafale dans $DELAI_SECONDES secondes..."
    Start-Sleep -Seconds $DELAI_SECONDES
}

Write-TITLE "======================================================"
Write-OK "Demo terminee ! $compteur requetes envoyees en $DUREE_MINUTES minutes."
Write-TITLE "======================================================"
