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
    
    processCapturedPhoto() {
        // Arrêter la caméra
        this.stopCamera();
        
        // Incrémenter le compteur
        this.photoCount++;
        this.updatePhotoCount();
        
        // Afficher l'image capturée
        const resultImage = document.getElementById('result-image');
        if (resultImage && this.capturedImage) {
            resultImage.src = URL.createObjectURL(this.capturedImage);
        }
        
        // Basculer vers l'interface de résultat
        this.showInterface('result');
        
        this.isCapturing = false;
        this.updateStatus('Photo capturée avec succès !');
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
                this.showAdminStatus('Connexion réussie !', 'success');
                setTimeout(() => this.hideAdminModal(), 1500);
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
