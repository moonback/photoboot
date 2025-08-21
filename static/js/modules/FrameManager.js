/**
 * Module de gestion des cadres pour le photobooth
 * Responsable de l'application des cadres sur les photos
 */
class FrameManager {
    constructor() {
        this.activeFrame = null;
        this.frameCache = new Map(); // Cache des cadres chargés
    }

    /**
     * Récupère le cadre actif depuis le serveur
     */
    async getActiveFrame() {
        try {
            const response = await fetch('/admin/frames/public/active');
            if (!response.ok) {
                console.log('Erreur lors de la récupération du cadre actif:', response.status);
                return null;
            }

            const frameData = await response.json();
            if (!frameData.frame) {
                console.log('Aucun cadre actif configuré');
                return null;
            }

            this.activeFrame = frameData.frame;
            console.log('Cadre actif récupéré:', this.activeFrame.name);
            return this.activeFrame;

        } catch (error) {
            console.error('Erreur lors de la récupération du cadre actif:', error);
            return null;
        }
    }

    /**
     * Applique le cadre actif à une image
     */
    async applyFrameToImage(imageBlob) {
        if (!this.activeFrame) {
            console.log('Aucun cadre actif disponible');
            return imageBlob;
        }

        try {
            console.log('Application du cadre:', this.activeFrame.name);

            // Créer un canvas temporaire pour appliquer le cadre
            const tempCanvas = document.createElement('canvas');
            const tempCtx = tempCanvas.getContext('2d');

            // Charger l'image capturée
            const img = await this.loadImageFromBlob(imageBlob);
            
            // Définir la taille du canvas
            tempCanvas.width = img.width;
            tempCanvas.height = img.height;

            // Dessiner la photo originale
            tempCtx.drawImage(img, 0, 0);

            // Charger et appliquer le cadre
            const frameImg = await this.loadFrameImage(this.activeFrame.filename);

            // Calculer la position et la taille du cadre
            const position = this.calculateFramePosition(this.activeFrame, img.width, img.height);
            const size = this.calculateFrameSize(this.activeFrame, img.width, img.height);

            console.log('=== DÉBOGAGE CADRE ===');
            console.log('Dimensions de la photo:', img.width, 'x', img.height);
            console.log('Dimensions du cadre original:', this.activeFrame.width, 'x', this.activeFrame.height);
            console.log('Taille demandée:', this.activeFrame.size + '%');
            console.log('Position calculée:', position);
            console.log('Taille calculée:', size);
            console.log('Position du cadre:', this.activeFrame.position);
            console.log('========================');

            // Appliquer le cadre
            this.drawFrameOnCanvas(tempCtx, frameImg, position, size, img.width, img.height);

            // Convertir le résultat en blob avec PNG pour préserver la transparence
            const newBlob = await this.canvasToBlob(tempCanvas);
            console.log('✅ Cadre appliqué avec succès en PNG');
            
            return newBlob;

        } catch (error) {
            console.error('Erreur lors de l\'application du cadre:', error);
            return imageBlob; // Retourner l'image originale en cas d'erreur
        }
    }

    /**
     * Charge une image depuis un blob
     */
    loadImageFromBlob(blob) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = URL.createObjectURL(blob);
        });
    }

    /**
     * Charge une image de cadre depuis le serveur
     */
    loadFrameImage(filename) {
        // Vérifier le cache d'abord
        if (this.frameCache.has(filename)) {
            return Promise.resolve(this.frameCache.get(filename));
        }

        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                this.frameCache.set(filename, img); // Mettre en cache
                resolve(img);
            };
            img.onerror = reject;
            img.src = `/frames/${filename}`;
        });
    }

    /**
     * Dessine le cadre sur le canvas
     */
    drawFrameOnCanvas(ctx, frameImg, position, size, photoWidth, photoHeight) {
        // Sauvegarder le contexte actuel
        ctx.save();

        // Définir le mode de composition pour préserver la transparence
        ctx.globalCompositeOperation = 'source-over';

        // S'assurer que le cadre couvre toute la photo pour un rendu bord à bord
        if (this.activeFrame.size >= 100) {
            // Mode bord à bord : le cadre couvre exactement la photo
            ctx.drawImage(frameImg, 0, 0, photoWidth, photoHeight);
        } else {
            // Mode redimensionné : positionner le cadre selon la configuration
            ctx.drawImage(frameImg, position.x, position.y, size.width, size.height);
        }

        // Restaurer le contexte
        ctx.restore();
    }

    /**
     * Convertit un canvas en blob
     */
    canvasToBlob(canvas) {
        return new Promise((resolve, reject) => {
            canvas.toBlob((blob) => {
                if (blob) {
                    resolve(blob);
                } else {
                    reject(new Error('Échec de la conversion en blob'));
                }
            }, 'image/png', 1.0); // Utiliser PNG pour préserver la transparence
        });
    }

    /**
     * Calcule la position du cadre
     */
    calculateFramePosition(frame, photoWidth, photoHeight) {
        const size = frame.size || 100;
        const finalSize = this.calculateFrameSize(frame, photoWidth, photoHeight);

        let x, y;
        switch (frame.position) {
            case 'top-left':
                x = 0; y = 0;
                break;
            case 'top-right':
                x = photoWidth - finalSize.width; y = 0;
                break;
            case 'bottom-left':
                x = 0; y = photoHeight - finalSize.height;
                break;
            case 'bottom-right':
                x = photoWidth - finalSize.width; y = photoHeight - finalSize.height;
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

        return { x: Math.round(x), y: Math.round(y) };
    }

    /**
     * Calcule la taille du cadre
     */
    calculateFrameSize(frame, photoWidth, photoHeight) {
        const size = frame.size || 100;

        // Pour un usage standard, le cadre doit couvrir toute la photo
        if (size >= 100) {
            return {
                width: photoWidth,
                height: photoHeight
            };
        }

        // Pour les tailles inférieures à 100%, calculer proportionnellement
        const scaleFactor = size / 100;
        const aspectRatio = photoWidth / photoHeight;

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

    /**
     * Vide le cache des cadres
     */
    clearCache() {
        this.frameCache.clear();
        console.log('Cache des cadres vidé');
    }

    /**
     * Vérifie si un cadre est actif
     */
    hasActiveFrame() {
        return this.activeFrame !== null;
    }

    /**
     * Obtient les informations du cadre actif
     */
    getActiveFrameInfo() {
        return this.activeFrame;
    }
}

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FrameManager;
} else {
    // Export global pour utilisation dans le navigateur
    window.FrameManager = FrameManager;
}
