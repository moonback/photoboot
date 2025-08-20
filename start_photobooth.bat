@echo off
echo ========================================
echo    PHOTOBOOTH - Demarrage
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python 3.8+ depuis python.org
    pause
    exit /b 1
)

REM Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo ERREUR: Impossible de créer l'environnement virtuel
        pause
        exit /b 1
    )
)

REM Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer/Mettre à jour les dépendances
echo Installation des dependances...
pip install -r requirements.txt

REM Créer le fichier .env s'il n'existe pas
if not exist "config\.env" (
    echo Creation du fichier de configuration...
    copy config\env.example config\.env
    echo.
    echo ATTENTION: Veuillez configurer config\.env avant de relancer
    echo.
    pause
)

REM Démarrer l'application
echo.
echo Demarrage de Photobooth...
echo URL: http://localhost:8000
echo Admin: Cliquer sur le bouton "Admin" en bas a gauche
echo.
echo Appuyez sur Ctrl+C pour arreter
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000

pause
