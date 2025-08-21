/**
 * Application Photobooth refactorisée et modulaire
 * Utilise des modules séparés pour une meilleure maintenabilité
 */

class PhotoboothApp {
    constructor() {
        // Initialiser les modules
        this.frameManager = new FrameManager();
        this.cameraManager = new CameraManager();
        this.photoManager = new PhotoManager();
        this.countdownManager = new CountdownManager();
        this.interfaceManager = new InterfaceManager();

        // État de l'application
        this.isCapturing = false;
        this.capturedImage = null;

        // Initialiser l'application
        this.init();
    }

    /**
     * Initialise l'application
     */
    async init() {
        try {
            console.log('Initialisation de l\'application Photobooth...');

            // Initialiser les modules
            this.interfaceManager.init();
            this.countdownManager.init(
                document.getElementById('countdown-number'),
                () => this.capturePhoto(), // Callback de fin
                (count) => console.log(`Compte à rebours: ${count}`) // Callback de tick
            );

            // Initialiser la caméra
            const videoElement = document.getElementById('camera-video');
            if (videoElement) {
                this.cameraManager.init(videoElement, () => this.capturePhoto());
            }

            // Récupérer le cadre actif
            await this.frameManager.getActiveFrame();

            // Lier les événements
            this.bindEvents();

            // Mettre à jour les statuts
            this.updateStatus('Système opérationnel');
            this.photoManager.updatePhotoCount();

            // Vérifier la santé du système
            await this.checkSystemHealth();

            console.log('✅ Application Photobooth initialisée avec succès');

        } catch (error) {
            console.error('❌ Erreur lors de l\'initialisation:', error);
            this.updateStatus('Erreur lors de l\'initialisation');
        }
    }

    /**
     * Lie les événements de l'interface
     */
    bindEvents() {
        // Bouton de démarrage principal
        const startButton = document.getElementById('start-button');
        if (startButton) {
            startButton.addEventListener('click', () => this.startCapture());
        }

        // Bouton admin
        const adminButton = document.getElementById('admin-button');
        if (adminButton) {
            adminButton.addEventListener('click', () => this.showAdminModal());
        }

        // Boutons de l'interface de capture
        const cancelButton = document.getElementById('cancel-capture');
        if (cancelButton) {
            cancelButton.addEventListener('click', () => this.cancelCapture());
        }

        const retakeButton = document.getElementById('retake-photo');
        if (retakeButton) {
            retakeButton.addEventListener('click', () => this.retakePhoto());
        }

        // Boutons de l'interface de résultat
        const newPhotoButton = document.getElementById('new-photo');
        if (newPhotoButton) {
            newPhotoButton.addEventListener('click', () => this.newPhoto());
        }

        const downloadButton = document.getElementById('download-photo');
        if (downloadButton) {
            downloadButton.addEventListener('click', () => this.downloadPhoto());
        }

        // Modal admin
        const closeAdminButton = document.getElementById('close-admin');
        if (closeAdminButton) {
            closeAdminButton.addEventListener('click', () => this.hideAdminModal());
        }

        const adminLoginButton = document.getElementById('admin-login');
        if (adminLoginButton) {
            adminLoginButton.addEventListener('click', () => this.adminLogin());
        }

        // Fermer la modal en cliquant à l'extérieur
        const adminModal = document.getElementById('admin-modal');
        if (adminModal) {
            adminModal.addEventListener('click', (e) => {
                if (e.target === adminModal) {
                    this.hideAdminModal();
                }
            });
        }

        // Gestion des touches clavier
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }

    /**
     * Démarre le processus de capture
     */
    async startCapture() {
        if (this.isCapturing) return;

        try {
            this.isCapturing = true;
            this.updateStatus('Préparation de la caméra...');

            // Démarrer la caméra
            await this.cameraManager.startCamera();

            // Basculer vers l'interface de capture
            this.interfaceManager.showInterface('capture');

            // Démarrer le compte à rebours
            this.countdownManager.startCountdown(3);

        } catch (error) {
            console.error('Erreur lors du démarrage de la capture:', error);
            this.updateStatus('Erreur: Impossible d\'accéder à la caméra');
            this.isCapturing = false;
        }
    }

    /**
     * Capture une photo
     */
    async capturePhoto() {
        try {
            this.updateStatus('Capture en cours...');

            // Capturer l'image depuis la caméra
            this.capturedImage = await this.cameraManager.captureFrame();

            // Traiter la photo capturée
            await this.processCapturedPhoto();

        } catch (error) {
            console.error('Erreur lors de la capture:', error);
            this.updateStatus('Erreur lors de la capture');
            this.cancelCapture();
        }
    }

    /**
     * Traite la photo capturée
     */
    async processCapturedPhoto() {
        try {
            // Arrêter la caméra
            this.cameraManager.stopCamera();

            // Appliquer le cadre actif si disponible
            if (this.frameManager.hasActiveFrame()) {
                this.capturedImage = await this.frameManager.applyFrameToImage(this.capturedImage);
            }

            // Afficher l'image capturée
            const resultImage = document.getElementById('result-image');
            if (resultImage && this.capturedImage) {
                resultImage.src = URL.createObjectURL(this.capturedImage);
            }

            // Sauvegarder la photo sur le serveur
            await this.photoManager.savePhotoToServer(this.capturedImage);

            // Transmettre la photo au gestionnaire d'impression/email
            this.transmitPhotoToPrintEmail();

            // Basculer vers l'interface de résultat
            this.interfaceManager.showInterface('result');

            this.isCapturing = false;
            this.updateStatus('Photo capturée et sauvegardée avec succès !');

        } catch (error) {
            console.error('Erreur lors du traitement de la photo:', error);
            this.updateStatus('Erreur lors du traitement de la photo');
            this.isCapturing = false;
        }
    }

    /**
     * Transmet la photo au gestionnaire d'impression/email
     */
    transmitPhotoToPrintEmail() {
        try {
            const currentPhoto = this.photoManager.getCurrentPhoto();
            if (window.printEmailManager && currentPhoto?.filename) {
                const photoPath = `uploads/${currentPhoto.filename}`;
                const photoUrl = `/uploads/${currentPhoto.filename}`;
                
                console.log('Transmission de la photo:', { photoPath, photoUrl });
                window.printEmailManager.setCurrentPhoto(photoPath, photoUrl);
                console.log('Photo transmise au gestionnaire d\'impression/email');
            }
        } catch (error) {
            console.error('Erreur lors de la transmission de la photo:', error);
        }
    }

    /**
     * Annule la capture
     */
    cancelCapture() {
        this.countdownManager.stopCountdown();
        this.cameraManager.stopCamera();
        this.interfaceManager.showInterface('main');
        this.isCapturing = false;
        this.updateStatus('Capture annulée');
    }

    /**
     * Reprend une nouvelle photo
     */
    retakePhoto() {
        this.interfaceManager.showInterface('main');
        this.capturedImage = null;
    }

    /**
     * Nouvelle photo
     */
    newPhoto() {
        this.interfaceManager.showInterface('main');
        this.capturedImage = null;
    }

    /**
     * Télécharge la photo
     */
    downloadPhoto() {
        if (this.capturedImage) {
            this.photoManager.downloadPhoto(this.capturedImage);
            this.updateStatus('Photo téléchargée');
        }
    }

    /**
     * Affiche la modal admin
     */
    showAdminModal() {
        const modal = document.getElementById('admin-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    /**
     * Masque la modal admin
     */
    hideAdminModal() {
        const modal = document.getElementById('admin-modal');
        if (modal) {
            modal.classList.add('hidden');
        }

        // Réinitialiser les champs
        const usernameInput = document.getElementById('admin-username');
        const passwordInput = document.getElementById('admin-password');
        if (usernameInput) usernameInput.value = '';
        if (passwordInput) passwordInput.value = '';

        // Masquer le statut
        const statusElement = document.getElementById('admin-status');
        if (statusElement) {
            statusElement.classList.add('hidden');
        }
    }

    /**
     * Connexion admin
     */
    async adminLogin() {
        const username = document.getElementById('admin-username')?.value;
        const password = document.getElementById('admin-password')?.value;
        const statusElement = document.getElementById('admin-status');

        if (!username || !password) {
            this.showAdminStatus('Veuillez remplir tous les champs', 'error');
            return;
        }

        try {
            const response = await fetch('/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const result = await response.json();

            if (result.success) {
                this.showAdminStatus('Connexion réussie ! Redirection...', 'success');
                setTimeout(() => {
                    this.hideAdminModal();
                    window.location.href = '/admin';
                }, 1500);
            } else {
                this.showAdminStatus(result.message || 'Échec de la connexion', 'error');
            }

        } catch (error) {
            console.error('Erreur lors de la connexion admin:', error);
            this.showAdminStatus('Erreur de connexion', 'error');
        }
    }

    /**
     * Affiche le statut admin
     */
    showAdminStatus(message, type) {
        const statusElement = document.getElementById('admin-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `admin-status ${type}`;
            statusElement.classList.remove('hidden');
        }
    }

    /**
     * Met à jour le statut
     */
    updateStatus(message) {
        const statusElement = document.getElementById('status-text');
        if (statusElement) {
            statusElement.textContent = message;
        }
    }

    /**
     * Met à jour le statut de la caméra
     */
    updateCameraStatus(isActive) {
        const statusElement = document.getElementById('camera-status');
        if (statusElement) {
            if (isActive) {
                statusElement.className = 'status-indicator bg-green-500';
                statusElement.querySelector('.status-text').textContent = 'Caméra ON';
            } else {
                statusElement.className = 'status-indicator bg-red-500';
                statusElement.querySelector('.status-text').textContent = 'Caméra';
            }
        }
    }

    /**
     * Vérifie la santé du système
     */
    async checkSystemHealth() {
        try {
            const response = await fetch('/health');
            const health = await response.json();

            if (health.status === 'healthy') {
                this.updateStatus('Système opérationnel');
                this.updateStorageStatus(true);
            } else {
                this.updateStatus('Problème système détecté');
                this.updateStorageStatus(false);
            }

        } catch (error) {
            console.error('Erreur lors de la vérification de santé:', error);
            this.updateStatus('Erreur de connexion au serveur');
            this.updateStorageStatus(false);
        }
    }

    /**
     * Met à jour le statut du stockage
     */
    updateStorageStatus(isHealthy) {
        const statusElement = document.getElementById('storage-status');
        if (statusElement) {
            if (isHealthy) {
                statusElement.className = 'status-indicator bg-green-500';
                statusElement.querySelector('.status-text').textContent = 'Stockage';
            } else {
                statusElement.className = 'status-indicator bg-red-500';
                statusElement.querySelector('.status-text').textContent = 'Stockage';
            }
        }
    }

    /**
     * Gère les touches clavier
     */
    handleKeyPress(event) {
        switch (event.key) {
            case 'Escape':
                if (this.interfaceManager.getCurrentInterface() === 'capture') {
                    this.cancelCapture();
                } else if (this.interfaceManager.getCurrentInterface() === 'result') {
                    this.newPhoto();
                }
                break;

            case 'Enter':
                if (this.interfaceManager.getCurrentInterface() === 'main') {
                    this.startCapture();
                }
                break;

            case 'F11':
                // Basculer le mode plein écran
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                } else {
                    document.exitFullscreen();
                }
                break;
        }
    }

    /**
     * Obtient le statut complet de l'application
     */
    getApplicationStatus() {
        return {
            isCapturing: this.isCapturing,
            currentInterface: this.interfaceManager.getCurrentInterface(),
            cameraStatus: this.cameraManager.getStatus(),
            countdownStatus: this.countdownManager.getStatus(),
            photoStats: this.photoManager.getPhotoStats(),
            hasActiveFrame: this.frameManager.hasActiveFrame(),
            frameInfo: this.frameManager.getActiveFrameInfo()
        };
    }

    /**
     * Réinitialise l'application
     */
    reset() {
        this.isCapturing = false;
        this.capturedImage = null;
        
        this.countdownManager.reset();
        this.cameraManager.stopCamera();
        this.interfaceManager.reset();
        this.photoManager.clearHistory();
        this.frameManager.clearCache();
        
        console.log('Application réinitialisée');
    }
}

// Initialisation de l'application quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    window.photoboothApp = new PhotoboothApp();
});

// Gestion des erreurs globales
window.addEventListener('error', (event) => {
    console.error('Erreur JavaScript:', event.error);
});

// Gestion des promesses rejetées
window.addEventListener('unhandledrejection', (event) => {
    console.error('Promesse rejetée non gérée:', event.reason);
});
