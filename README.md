# 📸 Photobooth

Application photobooth moderne avec backend FastAPI et interface web en plein écran, conçue pour Windows 10/11.

## 🚀 Fonctionnalités

### Étape 1 (Actuelle)
- ✅ **Backend FastAPI** avec architecture modulaire
- ✅ **Interface web** en plein écran avec design moderne
- ✅ **Système d'authentification admin** avec sessions sécurisées
- ✅ **Gestion de configuration** YAML + variables d'environnement
- ✅ **Logging avancé** avec rotation et rétention
- ✅ **API REST** complète avec documentation automatique
- ✅ **Stockage sécurisé** des fichiers avec validation
- ✅ **Tests unitaires** pour les endpoints critiques

### Étape 2 (Prévue)
- 🔄 **Capture vidéo** en temps réel
- 📷 **Prise de photos** automatique
- 🎨 **Filtres et effets** en temps réel

### Étape 3 (Prévue)
- 📧 **Envoi par email** des photos
- 🖨️ **Impression automatique** (Windows)
- 📱 **Interface mobile** responsive

## 🛠️ Installation Windows

### Prérequis
- **Python 3.8+** installé et dans le PATH
- **Git** pour cloner le projet
- **Powershell** ou **Command Prompt**

### 1. Cloner le projet
```powershell
git clone <url-du-repo>
cd photobooth
```

### 2. Créer l'environnement virtuel
```powershell
# Créer l'environnement
python -m venv venv

# Activer l'environnement
venv\Scripts\Activate.ps1

# Si vous avez des problèmes avec l'exécution de scripts PowerShell :
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Installer les dépendances
```powershell
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt
```

### 4. Configuration initiale
```powershell
# Copier le fichier d'exemple
copy config\env.example config\.env

# Éditer le fichier .env avec vos paramètres
notepad config\.env
```

**Variables importantes à configurer :**
```env
# Clé secrète (générer une clé aléatoire en production)
SECRET_KEY=votre-cle-secrete-ici

# Identifiants admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=votre-mot-de-passe

# Configuration serveur
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### 5. Lancer l'application
```powershell
# Démarrer le serveur
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Ou avec reload pour le développement
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Utilisation

### Interface utilisateur
- **URL principale** : `http://localhost:8000`
- **Interface admin** : Cliquer sur le bouton "⚙️ Admin" en bas à gauche
- **Documentation API** : `http://localhost:8000/docs` (en mode debug)

### Raccourcis clavier
- **F11** : Mode plein écran
- **Enter** : Démarrer la capture
- **Escape** : Annuler/Retour

### Endpoints API principaux
- `GET /health` - État de santé du système
- `GET /config` - Configuration actuelle
- `POST /admin/login` - Connexion administrateur
- `GET /status` - Statut général de l'application

## 🔧 Configuration

### Fichier config.yaml
```yaml
app:
  name: "Photobooth"
  version: "1.0.0"
  debug: false

server:
  host: "0.0.0.0"
  port: 8000

security:
  secret_key: "change-me-in-production"
  session_timeout: 3600
  bcrypt_rounds: 12

admin:
  username: "admin"
  password_hash: ""  # Sera défini via .env

storage:
  upload_dir: "uploads"
  max_file_size: 10485760  # 10MB
  allowed_extensions: [".jpg", ".jpeg", ".png", ".gif"]
```

### Variables d'environnement (.env)
Les variables d'environnement ont la priorité sur le fichier YAML :
- `SECRET_KEY` - Clé secrète pour les sessions
- `ADMIN_USERNAME` - Nom d'utilisateur admin
- `ADMIN_PASSWORD` - Mot de passe admin (hashé automatiquement)
- `HOST` - Adresse d'écoute du serveur
- `PORT` - Port du serveur
- `DEBUG` - Mode debug (true/false)

## 📁 Structure du projet

```
photoboot/
├── app/                    # Code source Python
│   ├── main.py           # Application principale FastAPI
│   ├── config.py         # Gestionnaire de configuration
│   ├── models.py         # Modèles Pydantic
│   ├── routes/           # Routes API
│   │   ├── health.py     # Endpoints de santé
│   │   ├── config_api.py # Gestion de la configuration
│   │   └── auth.py       # Authentification admin
│   ├── admin/            # Module d'administration
│   │   └── auth.py       # Gestion des sessions admin
│   └── storage/          # Gestion du stockage
│       └── files.py      # Opérations sur les fichiers
├── static/                # Fichiers statiques
│   ├── index.html        # Page principale
│   ├── css/style.css     # Styles CSS
│   └── js/app.js         # JavaScript frontend
├── config/                # Configuration
│   ├── config.yaml       # Configuration YAML
│   └── env.example       # Variables d'environnement
├── tests/                 # Tests unitaires
│   └── test_health.py    # Tests de santé
├── logs/                  # Fichiers de logs (créé automatiquement)
├── uploads/               # Dossier d'upload (créé automatiquement)
├── requirements.txt       # Dépendances Python
└── README.md             # Ce fichier
```

## 🧪 Tests

### Lancer les tests
```powershell
# Installer pytest si pas déjà fait
pip install pytest pytest-asyncio

# Lancer tous les tests
pytest

# Lancer un test spécifique
pytest tests/test_health.py

# Avec couverture (optionnel)
pip install pytest-cov
pytest --cov=app tests/
```

## 📝 Logs

Les logs sont automatiquement créés dans le dossier `logs/` :
- **Rotation** : 1 jour
- **Rétention** : 30 jours
- **Format** : Timestamp | Niveau | Module:Fonction:Ligne - Message

### Niveaux de log
- `DEBUG` : Informations détaillées (mode debug uniquement)
- `INFO` : Informations générales
- `WARNING` : Avertissements
- `ERROR` : Erreurs
- `CRITICAL` : Erreurs critiques

## 🔒 Sécurité

### Authentification admin
- **Sessions signées** avec `itsdangerous`
- **Hashage bcrypt** des mots de passe
- **Cookies HttpOnly** avec SameSite=Lax
- **Expiration automatique** des sessions

### Stockage des fichiers
- **Validation des extensions** autorisées
- **Limitation de taille** configurable
- **Noms de fichiers sécurisés** (pas de path traversal)
- **Nettoyage automatique** des anciens fichiers

## 🚨 Dépannage

### Problèmes courants

#### Erreur de port déjà utilisé
```powershell
# Vérifier les processus sur le port 8000
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID par l'ID du processus)
taskkill /PID <PID> /F
```

#### Erreur de permissions
```powershell
# Exécuter PowerShell en tant qu'administrateur
# Ou vérifier les permissions sur le dossier du projet
```

#### Problèmes de caméra
- Vérifier que la caméra n'est pas utilisée par une autre application
- Autoriser l'accès à la caméra dans les paramètres Windows
- Tester avec l'application Caméra Windows

#### Erreurs de configuration
```powershell
# Vérifier la syntaxe YAML
# Vérifier que le fichier .env est dans le bon dossier
# Vérifier les permissions sur les fichiers de config
```

### Logs d'erreur
```powershell
# Voir les logs en temps réel
Get-Content logs/photobooth.log -Wait

# Dernières erreurs
Get-Content logs/photobooth.log | Select-String "ERROR"
```

## 🔄 Mise à jour

### Mettre à jour le code
```powershell
git pull origin main
pip install -r requirements.txt --upgrade
```

### Redémarrer l'application
```powershell
# Arrêter le serveur (Ctrl+C)
# Relancer
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 Développement

### Mode debug
```powershell
# Activer le mode debug
$env:DEBUG="true"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Structure des routes
- **Health** : `/health/*` - Vérification de l'état du système
- **Config** : `/config/*` - Gestion de la configuration
- **Admin** : `/admin/*` - Authentification et administration

### Ajouter de nouvelles fonctionnalités
1. Créer les modèles dans `app/models.py`
2. Ajouter les routes dans `app/routes/`
3. Mettre à jour la configuration dans `config/config.yaml`
4. Ajouter les tests dans `tests/`

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- **Issues GitHub** : Pour les bugs et demandes de fonctionnalités
- **Documentation** : `/docs` quand l'application est en mode debug
- **Logs** : Vérifier le dossier `logs/` pour les erreurs

## 🔮 Roadmap

- [x] **Étape 1** : Backend FastAPI + Interface web de base
- [ ] **Étape 2** : Capture vidéo et photos
- [ ] **Étape 3** : Email et impression
- [ ] **Étape 4** : Interface mobile et partage
- [ ] **Étape 5** : Intelligence artificielle et filtres avancés

---

**Développé avec ❤️ pour Windows 10/11**
