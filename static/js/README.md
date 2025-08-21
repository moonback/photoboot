# 🏗️ Architecture Modulaire du Photobooth

## 📋 Vue d'ensemble

Le code JavaScript du photobooth a été refactorisé en plusieurs modules pour améliorer la **maintenabilité**, la **lisibilité** et la **réutilisabilité**. Chaque module a une responsabilité spécifique et peut être testé indépendamment.

## 🗂️ Structure des Modules

### 📁 `modules/` - Répertoire des modules

#### 🖼️ `FrameManager.js`
**Responsabilité** : Gestion des cadres et application sur les photos

**Fonctionnalités principales** :
- Récupération du cadre actif depuis le serveur
- Application des cadres sur les images
- Calcul des positions et tailles des cadres
- Cache des images de cadres pour optimiser les performances
- Gestion des erreurs et fallback

**Méthodes clés** :
```javascript
await frameManager.getActiveFrame()
await frameManager.applyFrameToImage(imageBlob)
frameManager.hasActiveFrame()
frameManager.clearCache()
```

#### 📹 `CameraManager.js`
**Responsabilité** : Gestion de la caméra et capture vidéo

**Fonctionnalités principales** :
- Démarrage/arrêt de la caméra
- Capture d'images depuis le flux vidéo
- Gestion des résolutions et changements de caméra
- Énumération des caméras disponibles
- Gestion des erreurs d'accès à la caméra

**Méthodes clés** :
```javascript
await cameraManager.startCamera()
await cameraManager.captureFrame()
cameraManager.stopCamera()
cameraManager.getStatus()
await cameraManager.getAvailableCameras()
```

#### 📸 `PhotoManager.js`
**Responsabilité** : Gestion des photos et historique

**Fonctionnalités principales** :
- Sauvegarde des photos sur le serveur
- Gestion de l'historique des photos
- Statistiques et métadonnées
- Export et gestion des photos
- Formatage des tailles et dates

**Méthodes clés** :
```javascript
await photoManager.savePhotoToServer(imageBlob)
photoManager.getPhotoHistory()
photoManager.getPhotoStats()
photoManager.exportHistory()
photoManager.clearHistory()
```

#### ⏰ `CountdownManager.js`
**Responsabilité** : Gestion du compte à rebours

**Fonctionnalités principales** :
- Démarrage/arrêt du compte à rebours
- Pause et reprise
- Callbacks de fin et de tick
- Gestion des transitions et animations
- Configuration de la durée

**Méthodes clés** :
```javascript
countdownManager.startCountdown(seconds)
countdownManager.pauseCountdown()
countdownManager.resumeCountdown()
countdownManager.stopCountdown()
countdownManager.getStatus()
```

#### 🖥️ `InterfaceManager.js`
**Responsabilité** : Gestion des interfaces utilisateur

**Fonctionnalités principales** :
- Navigation entre les interfaces
- Gestion des transitions
- Ajout/suppression dynamique d'interfaces
- Gestion des effets visuels
- État des interfaces

**Méthodes clés** :
```javascript
interfaceManager.showInterface('capture')
interfaceManager.getCurrentInterface()
interfaceManager.addInterface('test', 'elementId')
interfaceManager.getInterfaceStatus()
```

### 🚀 `app-refactored.js` - Application principale

**Responsabilité** : Orchestration des modules et logique métier

**Fonctionnalités principales** :
- Initialisation de tous les modules
- Gestion du flux de capture
- Liaison des événements utilisateur
- Gestion des erreurs globales
- Statut de l'application

## 🔧 Utilisation

### 1. Chargement des modules
```html
<!-- Charger les modules dans l'ordre -->
<script src="/static/js/modules/FrameManager.js"></script>
<script src="/static/js/modules/CameraManager.js"></script>
<script src="/static/js/modules/PhotoManager.js"></script>
<script src="/static/js/modules/CountdownManager.js"></script>
<script src="/static/js/modules/InterfaceManager.js"></script>

<!-- Charger l'application principale -->
<script src="/static/js/app-refactored.js"></script>
```

### 2. Utilisation dans le code
```javascript
// L'application est automatiquement initialisée
// Accès global via window.photoboothApp

// Exemple d'utilisation des modules
const app = window.photoboothApp;
const frameManager = app.frameManager;
const cameraManager = app.cameraManager;

// Vérifier le statut
const status = app.getApplicationStatus();
console.log('Statut de l\'application:', status);
```

## 🧪 Tests

### Page de test
Une page de test complète est disponible : `test-refactored.html`

**Fonctionnalités de test** :
- Test individuel de chaque module
- Vérification des statuts
- Test des fonctionnalités avancées
- Logs détaillés pour le débogage

### Tests unitaires
Chaque module peut être testé indépendamment :

```javascript
// Test FrameManager
const frameManager = new FrameManager();
const activeFrame = await frameManager.getActiveFrame();

// Test CameraManager
const cameraManager = new CameraManager();
const status = cameraManager.getStatus();

// Test PhotoManager
const photoManager = new PhotoManager();
const stats = photoManager.getPhotoStats();
```

## 📊 Avantages de la Refactorisation

### ✅ **Maintenabilité**
- Code organisé par responsabilité
- Facile de localiser et modifier une fonctionnalité
- Réduction de la complexité cyclomatique

### ✅ **Réutilisabilité**
- Modules utilisables dans d'autres projets
- API claire et documentée
- Peu de dépendances entre modules

### ✅ **Testabilité**
- Chaque module peut être testé indépendamment
- Mocking facile des dépendances
- Tests unitaires simplifiés

### ✅ **Évolutivité**
- Ajout de nouvelles fonctionnalités sans affecter l'existant
- Extension des modules existants
- Architecture extensible

### ✅ **Débogage**
- Logs détaillés par module
- Statuts clairs et accessibles
- Gestion d'erreurs granulaires

## 🔄 Migration

### Ancien code → Nouveau code
```javascript
// AVANT (monolithique)
this.applyActiveFrame();
this.startCamera();
this.startCountdown();

// APRÈS (modulaire)
await this.frameManager.applyFrameToImage(this.capturedImage);
await this.cameraManager.startCamera();
this.countdownManager.startCountdown(3);
```

### Compatibilité
- L'ancien fichier `app.js` reste fonctionnel
- La nouvelle version peut coexister
- Migration progressive possible

## 🚨 Gestion des Erreurs

Chaque module gère ses propres erreurs et fournit des informations détaillées :

```javascript
try {
    await frameManager.applyFrameToImage(imageBlob);
} catch (error) {
    console.error('Erreur FrameManager:', error);
    // Fallback : continuer sans cadre
}
```

## 📈 Performance

### Optimisations incluses
- Cache des images de cadres
- Gestion asynchrone des opérations
- Événements optimisés
- Nettoyage automatique des ressources

### Monitoring
```javascript
// Statut complet de l'application
const status = app.getApplicationStatus();
console.log('Performance:', status);
```

## 🔮 Évolutions Futures

### Modules prévus
- `PrintManager.js` - Gestion de l'impression
- `EmailManager.js` - Gestion des emails
- `ConfigManager.js` - Gestion de la configuration
- `LogManager.js` - Gestion des logs

### Améliorations
- Support des Web Workers pour les opérations lourdes
- Système de plugins
- API REST pour les modules
- Tests automatisés

## 📚 Documentation

### JSDoc
Tous les modules sont documentés avec JSDoc pour une meilleure intégration IDE.

### Exemples
Des exemples d'utilisation sont fournis dans chaque module.

### Support
Pour toute question sur l'architecture, consulter ce README ou les commentaires dans le code.
