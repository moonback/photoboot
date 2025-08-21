/**
 * Module de gestion de la caméra pour le photobooth
 * Responsable de l'accès à la caméra et de la capture vidéo
 */
class CameraManager {
    constructor() {
        this.stream = null;
        this.video = null;
        this.isActive = false;
        this.videoElement = null;
        this.onFrameCapture = null; // Callback pour la capture d'image
    }

    /**
     * Initialise le gestionnaire de caméra
     */
    init(videoElement, onFrameCapture) {
        this.videoElement = videoElement;
        this.onFrameCapture = onFrameCapture;
        console.log('Gestionnaire de caméra initialisé');
    }

    /**
     * Démarre la caméra
     */
    async startCamera() {
        try {
            if (this.isActive) {
                console.log('Caméra déjà active');
                return;
            }

            console.log('Démarrage de la caméra...');
            
            // Demander l'accès à la caméra
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                },
                audio: false
            });

            // Configurer l'élément vidéo
            if (this.videoElement) {
                this.videoElement.srcObject = this.stream;
                await this.videoElement.play();
                this.video = this.videoElement;
            }

            this.isActive = true;
            console.log('Caméra démarrée avec succès');

        } catch (error) {
            console.error('Erreur lors du démarrage de la caméra:', error);
            this.isActive = false;
            throw error;
        }
    }

    /**
     * Arrête la caméra
     */
    stopCamera() {
        try {
            if (this.stream) {
                this.stream.getTracks().forEach(track => track.stop());
                this.stream = null;
            }

            if (this.videoElement) {
                this.videoElement.srcObject = null;
            }

            this.isActive = false;
            this.video = null;
            console.log('Caméra arrêtée');

        } catch (error) {
            console.error('Erreur lors de l\'arrêt de la caméra:', error);
        }
    }

    /**
     * Capture une image depuis la caméra
     */
    async captureFrame() {
        if (!this.isActive || !this.video) {
            throw new Error('Caméra non active');
        }

        try {
            // Créer un canvas temporaire pour la capture
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            // Définir la taille du canvas selon la vidéo
            canvas.width = this.video.videoWidth;
            canvas.height = this.video.videoHeight;

            // Dessiner la vidéo sur le canvas
            ctx.drawImage(this.video, 0, 0);

            // Convertir en blob
            const blob = await this.canvasToBlob(canvas, 'image/jpeg', 0.9);
            
            console.log('Image capturée:', canvas.width, 'x', canvas.height);
            return blob;

        } catch (error) {
            console.error('Erreur lors de la capture:', error);
            throw error;
        }
    }

    /**
     * Convertit un canvas en blob
     */
    canvasToBlob(canvas, mimeType = 'image/jpeg', quality = 0.9) {
        return new Promise((resolve, reject) => {
            canvas.toBlob((blob) => {
                if (blob) {
                    resolve(blob);
                } else {
                    reject(new Error('Échec de la conversion en blob'));
                }
            }, mimeType, quality);
        });
    }

    /**
     * Vérifie si la caméra est active
     */
    isCameraActive() {
        return this.isActive;
    }

    /**
     * Obtient les dimensions de la vidéo
     */
    getVideoDimensions() {
        if (this.video) {
            return {
                width: this.video.videoWidth,
                height: this.video.videoHeight
            };
        }
        return null;
    }

    /**
     * Obtient le statut de la caméra
     */
    getStatus() {
        return {
            isActive: this.isActive,
            hasStream: !!this.stream,
            hasVideo: !!this.video,
            dimensions: this.getVideoDimensions()
        };
    }

    /**
     * Change la résolution de la caméra
     */
    async changeResolution(width, height) {
        if (!this.isActive) {
            throw new Error('Caméra non active');
        }

        try {
            // Arrêter la caméra actuelle
            this.stopCamera();

            // Redémarrer avec la nouvelle résolution
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: width },
                    height: { ideal: height },
                    facingMode: 'user'
                },
                audio: false
            });

            if (this.videoElement) {
                this.videoElement.srcObject = this.stream;
                await this.videoElement.play();
                this.video = this.videoElement;
            }

            this.isActive = true;
            console.log(`Résolution changée à ${width}x${height}`);

        } catch (error) {
            console.error('Erreur lors du changement de résolution:', error);
            throw error;
        }
    }

    /**
     * Obtient la liste des caméras disponibles
     */
    async getAvailableCameras() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            return devices.filter(device => device.kind === 'videoinput');
        } catch (error) {
            console.error('Erreur lors de l\'énumération des caméras:', error);
            return [];
        }
    }

    /**
     * Change de caméra
     */
    async switchCamera(deviceId) {
        if (!this.isActive) {
            throw new Error('Caméra non active');
        }

        try {
            // Arrêter la caméra actuelle
            this.stopCamera();

            // Démarrer la nouvelle caméra
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    deviceId: { exact: deviceId },
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            });

            if (this.videoElement) {
                this.videoElement.srcObject = this.stream;
                await this.videoElement.play();
                this.video = this.videoElement;
            }

            this.isActive = true;
            console.log('Caméra changée avec succès');

        } catch (error) {
            console.error('Erreur lors du changement de caméra:', error);
            throw error;
        }
    }
}

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CameraManager;
} else {
    // Export global pour utilisation dans le navigateur
    window.CameraManager = CameraManager;
}
