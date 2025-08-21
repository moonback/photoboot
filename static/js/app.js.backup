// Application JavaScript pour le photobooth

class PhotoboothApp {
    constructor() {
        this.currentInterface = 'main';
        this.photoCount = 0;
        this.isCapturing = false;
        this.countdownInterval = null;
        this.stream = null;
        this.video = null;
        this.canvas = null;
        this.capturedImage = null;

        this.init();
    }

    init() {
        this.bindEvents();
        this.updateStatus();
        this.checkSystemHealth();

        // Mettre à jour le compteur de photos
        this.updatePhotoCount();

        console.log('Photobooth initialisé');
    }

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

    async startCapture() {
        if (this.isCapturing) return;

        try {
            this.isCapturing = true;
            this.updateStatus('Préparation de la caméra...');

            // Démarrer la caméra
            await this.startCamera();

            // Basculer vers l'interface de capture
            this.showInterface('capture');

            // Démarrer le compte à rebours
            this.startCountdown();

        } catch (error) {
            console.error('Erreur lors du démarrage de la capture:', error);
            this.updateStatus('Erreur: Impossible d\'accéder à la caméra');
            this.isCapturing = false;
        }
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                },
                audio: false
            });

            this.video = document.getElementById('camera-video');
            if (this.video) {
                this.video.srcObject = this.stream;
                this.video.play();
            }

            // Mettre à jour le statut de la caméra
            this.updateCameraStatus(true);

        } catch (error) {
            console.error('Erreur lors de l\'accès à la caméra:', error);
            throw error;
        }
    }

    startCountdown() {
        let count = 3;
        const countdownElement = document.getElementById('countdown-number');

        if (countdownElement) {
            countdownElement.textContent = count;
        }

        this.countdownInterval = setInterval(() => {
            count--;

            if (countdownElement) {
                countdownElement.textContent = count;
            }

            if (count <= 0) {
                clearInterval(this.countdownInterval);
                this.capturePhoto();
            }
        }, 1000);
    }

    async capturePhoto() {
        try {
            this.updateStatus('Capture en cours...');

            // Créer le canvas pour la capture
            this.canvas = document.getElementById('capture-canvas');
            if (!this.canvas) {
                throw new Error('Canvas non trouvé');
            }

            const ctx = this.canvas.getContext('2d');
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;

            // Dessiner la vidéo sur le canvas
            ctx.drawImage(this.video, 0, 0);

            // Convertir en blob
            this.canvas.toBlob((blob) => {
                if (blob) {
                    this.capturedImage = blob;
                    this.processCapturedPhoto();
                }
            }, 'image/jpeg', 0.9);

        } catch (error) {
            console.error('Erreur lors de la capture:', error);
            this.updateStatus('Erreur lors de la capture');
            this.cancelCapture();
        }
    }

    async processCapturedPhoto() {
        // Arrêter la caméra
        this.stopCamera();

        // Incrémenter le compteur
        this.photoCount++;
        this.updatePhotoCount();

        // Appliquer le cadre actif si disponible
        await this.applyActiveFrame();

        // Afficher l'image capturée
        const resultImage = document.getElementById('result-image');
        if (resultImage && this.capturedImage) {
            resultImage.src = URL.createObjectURL(this.capturedImage);
        }

        // Sauvegarder la photo sur le serveur
        await this.savePhotoToServer();

        // Basculer vers l'interface de résultat
        this.showInterface('result');

        this.isCapturing = false;
        this.updateStatus('Photo capturée et sauvegardée avec succès !');
    }

    async applyActiveFrame() {
        try {
            // Récupérer le cadre actif via l'endpoint public
            const response = await fetch('/admin/frames/public/active');
            if (!response.ok) {
                console.log('Erreur lors de la récupération du cadre actif:', response.status);
                return;
            }

            const frameData = await response.json();
            if (!frameData.frame) {
                console.log('Aucun cadre actif configuré');
                return;
            }

            const frame = frameData.frame;
            console.log('Application du cadre:', frame.name);

            // Créer un canvas temporaire pour appliquer le cadre
            const tempCanvas = document.createElement('canvas');
            const tempCtx = tempCanvas.getContext('2d');

            // Créer une image à partir du blob capturé
            const img = new Image();

            // Attendre que l'image soit chargée
            await new Promise((resolve, reject) => {
                img.onload = resolve;
                img.onerror = reject;
                img.src = URL.createObjectURL(this.capturedImage);
            });

            // Définir la taille du canvas
            tempCanvas.width = img.width;
            tempCanvas.height = img.height;

            // Dessiner la photo originale
            tempCtx.drawImage(img, 0, 0);

            // Charger et appliquer le cadre
            const frameImg = new Image();

            // Attendre que le cadre soit chargé
            await new Promise((resolve, reject) => {
                frameImg.onload = resolve;
                frameImg.onerror = reject;
                frameImg.src = `/frames/${frame.filename}`;
            });

            // Calculer la position et la taille du cadre
            const position = this.calculateFramePosition(frame, img.width, img.height);
            const size = this.calculateFrameSize(frame, img.width, img.height);

            console.log('=== DÉBOGAGE CADRE ===');
            console.log('Dimensions de la photo:', img.width, 'x', img.height);
            console.log('Dimensions du cadre original:', frame.width, 'x', frame.height);
            console.log('Taille demandée:', frame.size + '%');
            console.log('Position calculée:', position);
            console.log('Taille calculée:', size);
            console.log('Position du cadre:', frame.position);
            console.log('========================');

            // IMPORTANT : Utiliser la composition pour préserver la transparence
            // Sauvegarder le contexte actuel
            tempCtx.save();

            // Définir le mode de composition pour préserver la transparence
            tempCtx.globalCompositeOperation = 'source-over';

            // S'assurer que le cadre couvre toute la photo pour un rendu bord à bord
            if (frame.size >= 100) {
                // Mode bord à bord : le cadre couvre exactement la photo
                tempCtx.drawImage(frameImg, 0, 0, img.width, img.height);
            } else {
                // Mode redimensionné : positionner le cadre selon la configuration
                tempCtx.drawImage(frameImg, position.x, position.y, size.width, size.height);
            }

            // Restaurer le contexte
            tempCtx.restore();

            // Convertir le résultat en blob avec PNG pour préserver la transparence
            const newBlob = await new Promise((resolve, reject) => {
                tempCanvas.toBlob((blob) => {
                    if (blob) {
                        resolve(blob);
                    } else {
                        reject(new Error('Échec de la conversion en blob'));
                    }
                }, 'image/png', 1.0); // Utiliser PNG pour préserver la transparence
            });

            // Mettre à jour l'image capturée avec le cadre appliqué
            this.capturedImage = newBlob;
            console.log('✅ Cadre appliqué avec succès en PNG');

        } catch (error) {
            console.error('Erreur lors de l\'application du cadre:', error);
            // Continuer sans cadre en cas d'erreur
        }
    }

    calculateFramePosition(frame, photoWidth, photoHeight) {
        let x, y;

        // Calculer d'abord la taille finale du cadre
        const finalSize = this.calculateFrameSize(frame, photoWidth, photoHeight);

        switch (frame.position) {
            case 'top-left':
                x = 0;
                y = 0;
                break;
            case 'top-right':
                x = photoWidth - finalSize.width;
                y = 0;
                break;
            case 'bottom-left':
                x = 0;
                y = photoHeight - finalSize.height;
                break;
            case 'bottom-right':
                x = photoWidth - finalSize.width;
                y = photoHeight - finalSize.height;
                break;
            case 'custom':
                x = (frame.x || 50) * photoWidth / 100;
                y = (frame.y || 50) * photoHeight / 100;
                break;
            default: // center
                x = (photoWidth - finalSize.width) / 2;
                y = (photoHeight - finalSize.height) / 2;
                break;
        }

        return { x, y };
    }

    calculateFrameSize(frame, photoWidth, photoHeight) {
        const size = frame.size || 100;

        // Pour un usage standard, le cadre doit couvrir toute la photo
        // Si la taille est 100% ou plus, utiliser les dimensions exactes de la photo
        if (size >= 100) {
            return {
                width: photoWidth,
                height: photoHeight
            };
        }

        // Pour les tailles inférieures à 100%, calculer proportionnellement
        // mais en gardant le ratio d'aspect de la photo
        const scaleFactor = size / 100;
        const aspectRatio = photoWidth / photoHeight;

        // Calculer la nouvelle taille en gardant le ratio d'aspect
        let newWidth, newHeight;
        if (photoWidth > photoHeight) {
            // Photo en mode paysage
            newWidth = photoWidth * scaleFactor;
            newHeight = newWidth / aspectRatio;
        } else {
            // Photo en mode portrait
            newHeight = photoHeight * scaleFactor;
            newWidth = newHeight * aspectRatio;
        }

        return {
            width: Math.round(newWidth),
            height: Math.round(newHeight)
        };
    }

    async savePhotoToServer() {
        if (!this.capturedImage) {
            console.error('Aucune image à sauvegarder');
            return;
        }

        try {
            this.updateStatus('Sauvegarde de la photo...');

            // Créer un FormData avec l'image
            const formData = new FormData();
            formData.append('photo', this.capturedImage, `photobooth_${Date.now()}.jpg`);

            // Envoyer la photo au serveur
            const response = await fetch('/upload/photo', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Photo sauvegardée:', result);
                this.updateStatus('Photo sauvegardée avec succès !');

                // Transmettre le chemin de la photo au gestionnaire d'impression/email
                console.log('=== TRANSMISSION DE LA PHOTO ===');
                console.log('Tentative de transmission de la photo...');
                console.log('window.printEmailManager existe:', !!window.printEmailManager);
                console.log('Type de window.printEmailManager:', typeof window.printEmailManager);
                console.log('result.filename:', result.filename);
                console.log('result complet:', result);

                if (window.printEmailManager && result.filename) {
                    const photoPath = `uploads/${result.filename}`;
                    const photoUrl = `/uploads/${result.filename}`;
                    console.log('Transmission de la photo:', { photoPath, photoUrl });
                    window.printEmailManager.setCurrentPhoto(photoPath, photoUrl);
                    console.log('Photo transmise au gestionnaire d\'impression/email:', photoPath);
                } else {
                    console.error('Impossible de transmettre la photo:', {
                        printEmailManagerExists: !!window.printEmailManager,
                        filename: result.filename,
                        printEmailManagerType: typeof window.printEmailManager
                    });
                }
                console.log('=== FIN TRANSMISSION ===');
            } else {
                console.error('Erreur lors de la sauvegarde:', response.status);
                this.updateStatus('Erreur lors de la sauvegarde de la photo');
            }

        } catch (error) {
            console.error('Erreur lors de la sauvegarde de la photo:', error);
            this.updateStatus('Erreur lors de la sauvegarde de la photo');
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        if (this.video) {
            this.video.srcObject = null;
        }

        this.updateCameraStatus(false);
    }

    cancelCapture() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
        }

        this.stopCamera();
        this.showInterface('main');
        this.isCapturing = false;
        this.updateStatus('Capture annulée');
    }

    retakePhoto() {
        this.showInterface('main');
        this.capturedImage = null;
    }

    newPhoto() {
        this.showInterface('main');
        this.capturedImage = null;
    }

    downloadPhoto() {
        if (this.capturedImage) {
            const url = URL.createObjectURL(this.capturedImage);
            const a = document.createElement('a');
            a.href = url;
            a.download = `photobooth_${Date.now()}.jpg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            this.updateStatus('Photo téléchargée');
        }
    }

    showInterface(interfaceName) {
        // Masquer toutes les interfaces
        const interfaces = ['main', 'capture', 'result'];
        interfaces.forEach(name => {
            const element = document.getElementById(`${name}-interface`);
            if (element) {
                element.classList.add('hidden');
            }
        });

        // Afficher l'interface demandée
        const targetInterface = document.getElementById(`${interfaceName}-interface`);
        if (targetInterface) {
            targetInterface.classList.remove('hidden');
            targetInterface.classList.add('fade-in');
        }

        this.currentInterface = interfaceName;
    }

    showAdminModal() {
        const modal = document.getElementById('admin-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

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
                    // Rediriger vers la page d'administration
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

    showAdminStatus(message, type) {
        const statusElement = document.getElementById('admin-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `admin-status ${type}`;
            statusElement.classList.remove('hidden');
        }
    }

    updateStatus(message) {
        const statusElement = document.getElementById('status-text');
        if (statusElement) {
            statusElement.textContent = message;
        }
    }

    updatePhotoCount() {
        const countElement = document.getElementById('photo-count');
        if (countElement) {
            countElement.textContent = this.photoCount;
        }
    }

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

    handleKeyPress(event) {
        switch (event.key) {
            case 'Escape':
                if (this.currentInterface === 'capture') {
                    this.cancelCapture();
                } else if (this.currentInterface === 'result') {
                    this.newPhoto();
                }
                break;

            case 'Enter':
                if (this.currentInterface === 'main') {
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
