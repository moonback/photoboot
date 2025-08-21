// Configuration générale de l'application
const APP_CONFIG = {
    // Nom de l'application
    name: "Photo Studio Pro",

    // Version
    version: "1.0.0",

    // Description
    description: "Prêt à capturer vos moments !",

    // Paramètres de l'interface
    interface: {
        // Titre principal
        mainTitle: "📸 Photo Studio Pro",

        // Sous-titre
        subtitle: "Prêt à capturer vos moments !",

        // Bouton de démarrage
        startButtonText: "DÉMARRER",

        // Messages
        messages: {
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
        }
    },

    // Paramètres de la caméra
    camera: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'user'
    },

    // Paramètres des photos
    photo: {
        format: 'png',
        quality: 1.0,
        filenamePrefix: 'photo_studio_'
    }
};

// Fonction pour mettre à jour dynamiquement l'interface
function updateInterfaceWithConfig() {
    // Titre principal
    const mainTitle = document.querySelector('#main-interface h1');
    if (mainTitle) {
        mainTitle.innerHTML = APP_CONFIG.interface.mainTitle;
    }

    // Sous-titre
    const subtitle = document.querySelector('#main-interface p');
    if (subtitle) {
        subtitle.textContent = APP_CONFIG.interface.subtitle;
    }

    // Bouton de démarrage
    const startButton = document.querySelector('#start-button .btn-text');
    if (startButton) {
        startButton.textContent = APP_CONFIG.interface.startButtonText;
    }

    // Version
    const versionText = document.getElementById('version-text');
    if (versionText) {
        versionText.textContent = `Version ${APP_CONFIG.version}`;
    }

    // Titre de la page
    document.title = APP_CONFIG.name;

    // Interface de capture
    const captureTitle = document.querySelector('#capture-interface h2');
    if (captureTitle) {
        captureTitle.textContent = APP_CONFIG.interface.messages.prepare;
    }

    const captureSubtitle = document.querySelector('#capture-interface p');
    if (captureSubtitle) {
        captureSubtitle.textContent = APP_CONFIG.interface.messages.countdown;
    }

    // Interface de résultat
    const resultTitle = document.querySelector('#result-interface h2');
    if (resultTitle) {
        resultTitle.textContent = APP_CONFIG.interface.messages.photoTaken;
    }

    const resultSubtitle = document.querySelector('#result-interface p');
    if (resultSubtitle) {
        resultSubtitle.textContent = APP_CONFIG.interface.messages.photoReady;
    }

    // Boutons
    const newPhotoButton = document.getElementById('new-photo');
    if (newPhotoButton) {
        newPhotoButton.innerHTML = `📸 ${APP_CONFIG.interface.messages.newPhoto}`;
    }

    const downloadButton = document.getElementById('download-photo');
    if (downloadButton) {
        downloadButton.innerHTML = `💾 ${APP_CONFIG.interface.messages.download}`;
    }

    const cancelButton = document.getElementById('cancel-capture');
    if (cancelButton) {
        cancelButton.innerHTML = `❌ ${APP_CONFIG.interface.messages.cancel}`;
    }

    const retakeButton = document.getElementById('retake-photo');
    if (retakeButton) {
        retakeButton.innerHTML = `🔄 ${APP_CONFIG.interface.messages.retake}`;
    }
}

// Exporter la configuration
window.APP_CONFIG = APP_CONFIG;
window.updateInterfaceWithConfig = updateInterfaceWithConfig;
