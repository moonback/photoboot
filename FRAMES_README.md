# Gestion des Cadres - Photobooth

## Vue d'ensemble

Cette fonctionnalité permet aux administrateurs d'ajouter des cadres superposés sur les photos prises par le photobooth. Les cadres sont des images PNG avec transparence qui sont appliqués automatiquement sur chaque photo capturée.

## Fonctionnalités

### Pour l'Administrateur

1. **Ajout de cadres** : Upload d'images PNG avec transparence
2. **Configuration de position** : 6 positions prédéfinies + position personnalisée
3. **Ajustement de taille** : Taille du cadre de 10% à 200% de la taille originale
4. **Prévisualisation en temps réel** : Voir le résultat avant de sauvegarder
5. **Gestion des cadres** : Activer/désactiver, supprimer, modifier

### Pour l'Utilisateur

1. **Application automatique** : Le cadre actif est automatiquement appliqué sur chaque photo
2. **Transparence préservée** : Les cadres PNG avec transparence s'intègrent naturellement

## Utilisation

### 1. Accès à la Gestion des Cadres

1. Connectez-vous à l'interface d'administration (`/admin`)
2. Cliquez sur "🖼️ Gestion des cadres" dans le menu de gauche

### 2. Ajout d'un Nouveau Cadre

1. **Nom** : Donnez un nom descriptif au cadre
2. **Description** : Description optionnelle du cadre
3. **Fichier** : Sélectionnez un fichier PNG avec transparence
4. **Position** : Choisissez parmi :
   - Centré (par défaut)
   - Haut-gauche
   - Haut-droite
   - Bas-gauche
   - Bas-droite
   - Personnalisé (avec coordonnées X/Y en pourcentage)
5. **Taille** : Ajustez la taille du cadre (10% à 200%)
6. **Actif** : Cochez pour activer ce cadre par défaut

### 3. Prévisualisation

- La prévisualisation se met à jour automatiquement
- Utilise une photo d'exemple pour montrer le rendu
- Affiche la position et la taille exactes du cadre

### 4. Gestion des Cadres

- **Prévisualiser** : Voir le rendu du cadre
- **Activer** : Rendre ce cadre actif (désactive automatiquement les autres)
- **Supprimer** : Supprimer définitivement le cadre

## Spécifications Techniques

### Format des Fichiers

- **Type** : PNG uniquement
- **Transparence** : Support complet de la transparence
- **Taille recommandée** : 1920x1080 pixels
- **Poids** : Maximum 10MB

### Positions Prédéfinies

- **Center** : Centré sur la photo
- **Top-left** : Coin supérieur gauche
- **Top-right** : Coin supérieur droit
- **Bottom-left** : Coin inférieur gauche
- **Bottom-right** : Coin inférieur droit
- **Custom** : Position personnalisée avec coordonnées X/Y

### Stockage

- **Fichiers** : Dossier `frames/`
- **Configuration** : `config/frames.json`
- **Métadonnées** : ID unique, nom, description, position, taille, etc.

## API Endpoints

### GET /admin/frames
Récupère la liste de tous les cadres

### GET /admin/frames/active
Récupère le cadre actuellement actif

### POST /admin/frames
Crée un nouveau cadre

### GET /admin/frames/{frame_id}
Récupère un cadre spécifique

### POST /admin/frames/{frame_id}/toggle
Active/désactive un cadre

### DELETE /admin/frames/{frame_id}
Supprime un cadre

### GET /frames/{filename}
Sert le fichier d'un cadre

## Intégration avec la Capture

1. **Capture** : Photo prise normalement
2. **Application du cadre** : Le cadre actif est automatiquement appliqué
3. **Sauvegarde** : Photo avec cadre intégré sauvegardée
4. **Affichage** : Résultat final affiché à l'utilisateur

## Bonnes Pratiques

### Création de Cadres

1. **Transparence** : Utilisez des PNG avec fond transparent
2. **Résolution** : Créez des cadres en haute résolution
3. **Design** : Pensez à l'intégration avec différents types de photos
4. **Taille** : Testez différentes tailles pour un rendu optimal

### Gestion

1. **Un seul cadre actif** : Un seul cadre peut être actif à la fois
2. **Sauvegarde** : Sauvegardez régulièrement vos cadres
3. **Test** : Testez les cadres avant de les activer en production

## Dépannage

### Problèmes Courants

1. **Cadre non visible** : Vérifiez que le cadre est actif
2. **Position incorrecte** : Ajustez la position et la taille
3. **Fichier corrompu** : Re-upload du fichier PNG
4. **Performance** : Réduisez la taille des fichiers si nécessaire

### Logs

Les opérations sur les cadres sont loggées dans les logs système :
- Création de cadres
- Activation/désactivation
- Suppression
- Erreurs d'upload

## Sécurité

- **Validation des fichiers** : Seuls les PNG sont acceptés
- **Limitation de taille** : Maximum 10MB par fichier
- **Authentification** : Seuls les administrateurs peuvent gérer les cadres
- **Isolation** : Les fichiers sont stockés dans un dossier séparé

## Support

Pour toute question ou problème avec la gestion des cadres :
1. Vérifiez les logs système
2. Testez avec un fichier PNG simple
3. Vérifiez la configuration dans `config/frames.json`
4. Contactez l'administrateur système
