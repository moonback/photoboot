# 🎨 Guide de Personnalisation de l'Application

## 📝 Changer le Nom de l'Application

### **Étape 1 : Modifier le Fichier de Configuration**

Ouvrez le fichier `static/js/custom-config.js` et modifiez la ligne suivante :

```javascript
// Nom de votre application (sera affiché partout)
const CUSTOM_APP_NAME = "Photo Studio Pro";
```

**Exemples de noms personnalisés :**
- `"Studio Photo Élégance"`
- `"Photo Booth Premium"`
- `"Capture d'Instants"`
- `"Photo Studio Deluxe"`
- `"Instantanés Pro"`

### **Étape 2 : Personnaliser l'Icône**

Vous pouvez changer l'emoji qui apparaît avec le nom :

```javascript
// Icône principale (emoji)
const CUSTOM_APP_ICON = "📸";
```

**Autres emojis disponibles :**
- 🎭 `"Studio Photo Élégance"`
- ✨ `"Photo Booth Premium"`
- 🌟 `"Capture d'Instants"`
- 💎 `"Photo Studio Deluxe"`
- 🎪 `"Instantanés Pro"`

### **Étape 3 : Modifier la Description**

Personnalisez le sous-titre de l'application :

```javascript
// Description de votre application
const CUSTOM_APP_DESCRIPTION = "Prêt à capturer vos moments !";
```

**Exemples de descriptions :**
- `"Vos souvenirs en un clic !"`
- `"L'art de la photographie instantanée"`
- `"Créez des souvenirs inoubliables"`
- `"La magie de l'instant présent"`
- `"Votre studio photo portable"`

## 🎯 Autres Personnalisations Disponibles

### **Messages de l'Interface**

Vous pouvez personnaliser tous les textes de l'application :

```javascript
const CUSTOM_MESSAGES = {
    systemReady: "Système prêt",
    photoTaken: "Photo prise !",
    photoReady: "Votre photo est prête",
    // ... autres messages
};
```

### **Couleurs du Thème**

Personnalisez les couleurs de l'interface :

```javascript
const CUSTOM_THEME_COLORS = {
    primary: "from-blue-400 to-purple-600",
    secondary: "from-green-400 to-blue-600",
    accent: "from-pink-400 to-red-600"
};
```

### **Paramètres de la Caméra**

Ajustez la qualité de la caméra :

```javascript
const CUSTOM_CAMERA_SETTINGS = {
    width: { ideal: 1920 },  // Haute définition
    height: { ideal: 1080 }, // Full HD
    facingMode: 'user'
};
```

## 🚀 Comment Appliquer les Changements

### **Méthode 1 : Rechargement de la Page**
1. Modifiez le fichier `custom-config.js`
2. Sauvegardez le fichier
3. Rechargez la page dans votre navigateur

### **Méthode 2 : Rechargement Dynamique**
Dans la console du navigateur, tapez :
```javascript
reloadCustomConfig();
```

## 📁 Fichiers à Modifier

### **Fichier Principal :**
- `static/js/custom-config.js` ← **MODIFIEZ CELUI-CI**

### **Fichiers de Support :**
- `static/js/config.js` (ne pas modifier)
- `static/index.html` (ne pas modifier)

## 💡 Conseils de Personnalisation

### **1. Nom de l'Application**
- **Court et mémorable** : Maximum 20 caractères
- **Professionnel** : Évitez les termes trop familiers
- **Unique** : Distinguez-vous de la concurrence

### **2. Icône**
- **Cohérent** : Choisissez un emoji qui correspond à votre activité
- **Visible** : Assurez-vous qu'il s'affiche bien sur tous les appareils
- **Significatif** : L'icône doit représenter votre service

### **3. Description**
- **Claire** : Expliquez rapidement ce que fait l'application
- **Attractive** : Donnez envie d'utiliser le service
- **Courte** : Maximum 50 caractères

## 🔧 Exemple Complet de Personnalisation

```javascript
// ========================================
// CONFIGURATION PERSONNALISABLE
// ========================================

// Nom de votre application
const CUSTOM_APP_NAME = "Studio Photo Élégance";

// Version de votre application
const CUSTOM_APP_VERSION = "2.0.0";

// Description de votre application
const CUSTOM_APP_DESCRIPTION = "L'art de la photographie instantanée";

// Icône principale
const CUSTOM_APP_ICON = "🎭";

// Messages personnalisés
const CUSTOM_MESSAGES = {
    systemReady: "Studio prêt",
    photoTaken: "Chef-d'œuvre créé !",
    photoReady: "Votre œuvre est prête",
    // ... autres messages
};
```

## ✅ Vérification des Changements

Après modification, vérifiez que :

1. ✅ **Titre de la page** : Le nom de l'application apparaît dans l'onglet du navigateur
2. ✅ **Titre principal** : Le nom s'affiche en grand sur la page d'accueil
3. ✅ **Sous-titre** : La description personnalisée est visible
4. ✅ **Console** : Le message de confirmation s'affiche

## 🆘 Dépannage

### **Problème : Les changements ne s'appliquent pas**
**Solution :**
1. Vérifiez que le fichier est sauvegardé
2. Videz le cache du navigateur (Ctrl+F5)
3. Vérifiez la console pour les erreurs

### **Problème : L'interface ne se met pas à jour**
**Solution :**
1. Rechargez complètement la page
2. Utilisez `reloadCustomConfig()` dans la console
3. Vérifiez l'ordre des scripts dans le HTML

---

**💡 Conseil Final** : Commencez par changer le nom de l'application, puis personnalisez progressivement les autres éléments. Testez après chaque modification pour vous assurer que tout fonctionne correctement.
