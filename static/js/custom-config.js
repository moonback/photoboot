// ========================================
// CONFIGURATION PERSONNALISABLE
// ========================================
// Modifiez les valeurs ci-dessous pour personnaliser votre application

// Nom de votre application (sera affiché partout)
const CUSTOM_APP_NAME = "PhotoBooth Esil";

// Version de votre application
const CUSTOM_APP_VERSION = "1.0.0";

// Description de votre application
const CUSTOM_APP_DESCRIPTION = "Prêt à capturer vos moments !";

// Icône principale (emoji)
const CUSTOM_APP_ICON = "📸";

// Couleurs du thème (optionnel)
const CUSTOM_THEME_COLORS = {
    primary: "from-blue-400 to-purple-600",
    secondary: "from-green-400 to-blue-600",
    accent: "from-pink-400 to-red-600"
};

// Messages personnalisés
const CUSTOM_MESSAGES = {
    systemReady: "Système prêt",
    preparingCamera: "Préparation de la caméra...",
    captureInProgress: "Capture en cours...",
    photoTaken: "Photo prise !",
    photoReady: "Votre photo est prête",
    photoSaved: "Photo capturée et sauvegardée avec succès !",
    photoDownloaded: "Photo téléchargée",
    newPhoto: "Nouvelle photo",
    download: "Télécharger",
    cancel: "Annuler",
    retake: "Reprendre",
    prepare: "Préparez-vous !",
    countdown: "La photo sera prise dans"
};

// Paramètres de la caméra
const CUSTOM_CAMERA_SETTINGS = {
    width: { ideal: 1280 },
    height: { ideal: 720 },
    facingMode: 'user'
};

// Paramètres des photos
const CUSTOM_PHOTO_SETTINGS = {
    format: 'png',
    quality: 1.0,
    filenamePrefix: 'photo_studio_'
};

// ========================================
// NE MODIFIEZ PAS LE CODE CI-DESSOUS
// ========================================

// Application de la configuration personnalisée
const PERSONALIZED_CONFIG = {
    name: CUSTOM_APP_NAME,
    version: CUSTOM_APP_VERSION,
    description: CUSTOM_APP_DESCRIPTION,
    interface: {
        mainTitle: `${CUSTOM_APP_ICON} ${CUSTOM_APP_NAME}`,
        subtitle: CUSTOM_APP_DESCRIPTION,
        startButtonText: "DÉMARRER",
        messages: CUSTOM_MESSAGES
    },
    camera: CUSTOM_CAMERA_SETTINGS,
    photo: CUSTOM_PHOTO_SETTINGS
};

// Mise à jour de la configuration principale
if (window.APP_CONFIG) {
    Object.assign(window.APP_CONFIG, PERSONALIZED_CONFIG);

    // Mise à jour de l'interface si elle est déjà chargée
    if (window.updateInterfaceWithConfig) {
        window.updateInterfaceWithConfig();
    }
}

// Fonction pour recharger la configuration
window.reloadCustomConfig = function () {
    if (window.updateInterfaceWithConfig) {
        window.updateInterfaceWithConfig();
    }
};

console.log(`✅ Configuration personnalisée chargée pour: ${CUSTOM_APP_NAME}`);
