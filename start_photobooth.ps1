# Script PowerShell pour démarrer Photobooth
# Exécuter en tant qu'administrateur si nécessaire

param(
    [switch]$Dev,
    [switch]$Install,
    [switch]$Test,
    [int]$Port = 8000
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    PHOTOBOOTH - Démarrage PowerShell" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Python est installé
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERREUR: Python n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    Write-Host "Veuillez installer Python 3.8+ depuis python.org" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

# Vérifier si l'environnement virtuel existe
if (-not (Test-Path "venv")) {
    Write-Host "Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ ERREUR: Impossible de créer l'environnement virtuel" -ForegroundColor Red
        Read-Host "Appuyez sur Entrée pour continuer"
        exit 1
    }
    Write-Host "✓ Environnement virtuel créé" -ForegroundColor Green
}

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Installer/Mettre à jour les dépendances
if ($Install -or (-not (Test-Path "venv\Lib\site-packages\fastapi"))) {
    Write-Host "Installation des dépendances..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ ERREUR: Impossible d'installer les dépendances" -ForegroundColor Red
        Read-Host "Appuyez sur Entrée pour continuer"
        exit 1
    }
    Write-Host "✓ Dépendances installées" -ForegroundColor Green
}

# Créer le fichier .env s'il n'existe pas
if (-not (Test-Path "config\.env")) {
    Write-Host "Création du fichier de configuration..." -ForegroundColor Yellow
    Copy-Item "config\env.example" "config\.env"
    Write-Host "⚠️  ATTENTION: Veuillez configurer config\.env avant de relancer" -ForegroundColor Yellow
    Write-Host "Variables importantes: SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD" -ForegroundColor Yellow
    Write-Host ""
}

# Lancer les tests si demandé
if ($Test) {
    Write-Host "Lancement des tests..." -ForegroundColor Yellow
    pip install pytest pytest-asyncio
    python -m pytest tests/ -v
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Certains tests ont échoué" -ForegroundColor Yellow
    } else {
        Write-Host "✓ Tous les tests passent" -ForegroundColor Green
    }
    Write-Host ""
}

# Démarrer l'application
Write-Host "Démarrage de Photobooth..." -ForegroundColor Green
Write-Host "URL: http://localhost:$Port" -ForegroundColor Cyan
Write-Host "Admin: Cliquer sur le bouton 'Admin' en bas à gauche" -ForegroundColor Cyan
Write-Host "Documentation API: http://localhost:$Port/docs" -ForegroundColor Cyan
Write-Host ""

if ($Dev) {
    Write-Host "Mode développement activé (reload automatique)" -ForegroundColor Yellow
    Write-Host "Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow
    Write-Host ""
    uvicorn app.main:app --host 0.0.0.0 --port $Port --reload
} else {
    Write-Host "Mode production" -ForegroundColor Yellow
    Write-Host "Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow
    Write-Host ""
    uvicorn app.main:app --host 0.0.0.0 --port $Port
}

Read-Host "Appuyez sur Entrée pour continuer"
