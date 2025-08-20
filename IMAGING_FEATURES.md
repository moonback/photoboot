# Fonctionnalités d'Imagerie du Photobooth

## Vue d'ensemble

Ce document décrit les fonctionnalités d'imagerie avancées du photobooth, incluant la gestion des cadres, la mise en page d'impression et l'interface utilisateur améliorée.

## 🖼️ Cadres et Superposition

### Dossier des cadres
- **Emplacement** : `app/imaging/frames/`
- **Format** : Images PNG avec transparence
- **Exemple** : `default.png` (cadre par défaut)

### Fonctionnalités des cadres
- **Superposition PNG** : Les cadres sont superposés sur les photos
- **Texte paramétrable** : Police libre, placement, alignement et couleur configurables
- **Opacité ajustable** : Contrôle de la transparence du cadre

## 🖨️ Mise en Page d'Impression

### Templates disponibles
- **Strip 2x6** : Bande de photos 2x6 pouces (152.4 x 50.8 mm)
- **Postcard 4x6** : Carte postale 4x6 pouces (101.6 x 152.4 mm)

### Paramètres des templates
- **Marges** : Configurables en millimètres
- **Grille** : Disposition en colonnes et lignes
- **DPI** : 300 DPI pour une qualité d'impression optimale
- **Bordures** : Épaisseur et coins arrondis configurables

### Fichiers de configuration
- **Emplacement** : `app/imaging/printing/templates/`
- **Format** : JSON avec structure standardisée
- **Exemple** : `strip_2x6.json`, `postcard_4x6.json`

## 🎯 Interface Utilisateur

### Modes de capture
- **Mode simple** : Capture d'une seule photo
- **Mode multi** : Capture de 4 photos consécutives

### Filtres disponibles
- **Aucun** : Photo originale
- **Vintage** : Effet sépia
- **N&B** : Noir et blanc
- **Chaud** : Tons chauds

### Compte à rebours
- **Décompte** : 3-2-1 avant capture
- **Progression** : Indicateur visuel pour le mode multi
- **Aperçu** : Prévisualisation en temps réel

### Écran de validation
- **Aperçu** : Grille des photos capturées
- **Actions** : Reprendre ou valider
- **Composition** : Sélection du format d'impression

## 🔧 Architecture Technique

### Module de mise en page
- **Fichier** : `app/imaging/layout.py`
- **Classe principale** : `PrintLayout`
- **Fonctionnalités** :
  - Chargement des templates JSON
  - Composition des photos selon la mise en page
  - Application des cadres et du texte
  - Génération des miniatures

### API de composition
- **Route** : `/api/compose`
- **Méthode** : POST
- **Paramètres** :
  - `photos` : Liste des photos (FormData)
  - `template` : Nom du template
  - `text_overlay` : Texte à superposer (optionnel)
  - `frame_name` : Nom du cadre (optionnel)

### Endpoints disponibles
- `POST /api/compose` : Créer une composition
- `GET /api/templates` : Lister les templates
- `GET /api/templates/{name}` : Détails d'un template
- `GET /api/frames` : Lister les cadres disponibles
- `GET /api/download/{filename}` : Télécharger une composition

## 📁 Structure des dossiers

```
app/imaging/
├── frames/                 # Cadres PNG
│   └── default.png
├── printing/              # Templates d'impression
│   └── templates/
│       ├── strip_2x6.json
│       └── postcard_4x6.json
└── layout.py              # Module de mise en page

data/
├── photos/                # Photos capturées
├── prints/                # Compositions générées
└── thumbs/                # Miniatures

static/
├── css/style.css          # Styles CSS
├── js/app.js              # JavaScript principal
└── index.html             # Interface utilisateur
```

## 🚀 Utilisation

### 1. Capture des photos
1. Sélectionner le mode (simple ou multi)
2. Choisir un filtre
3. Cliquer sur "DÉMARRER"
4. Attendre le compte à rebours
5. Les photos sont capturées automatiquement

### 2. Validation et composition
1. Apercevoir les photos capturées
2. Cliquer sur "Valider"
3. Choisir le format d'impression
4. Ajouter du texte personnalisé (optionnel)
5. Cliquer sur "Générer"

### 3. Téléchargement
- La composition est générée automatiquement
- Le fichier PNG final est téléchargé
- Une miniature est créée pour l'aperçu

## ⚙️ Configuration

### Ajouter un nouveau template
1. Créer un fichier JSON dans `app/imaging/printing/templates/`
2. Définir les paramètres de dimensions, marges et mise en page
3. Redémarrer l'application

### Ajouter un nouveau cadre
1. Placer l'image PNG dans `app/imaging/frames/`
2. Utiliser la transparence pour les zones transparentes
3. Le cadre sera automatiquement disponible

### Personnaliser les filtres
- Modifier la fonction `applyFilter()` dans `app.js`
- Ajouter de nouveaux algorithmes de traitement d'image
- Mettre à jour l'interface utilisateur

## 🧪 Tests

### Exécuter les tests
```bash
pytest tests/test_layout.py -v
```

### Tests disponibles
- Chargement des templates
- Composition avec une ou plusieurs photos
- Application du texte superposé
- Gestion des erreurs

## 🔍 Dépannage

### Problèmes courants
1. **Cadre non trouvé** : Vérifier le nom du fichier dans `app/imaging/frames/`
2. **Template invalide** : Vérifier la syntaxe JSON du template
3. **Erreur de composition** : Vérifier les permissions du dossier `data/prints/`

### Logs
- Les erreurs sont enregistrées dans les logs de l'application
- Utiliser `loguru` pour le débogage
- Vérifier les permissions des dossiers

## 📈 Améliorations futures

- **Filtres avancés** : Effets artistiques supplémentaires
- **Templates dynamiques** : Création via l'interface d'administration
- **Export multiple** : Formats TIFF, PDF
- **Prévisualisation en temps réel** : Aperçu de la composition avant génération
- **Gestion des polices** : Support de polices personnalisées
- **Calibration d'impression** : Profils de couleur ICC
