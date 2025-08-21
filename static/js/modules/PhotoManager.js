/**
 * Module de gestion des photos pour le photobooth
 * Responsable de la sauvegarde et de la gestion des photos
 */
class PhotoManager {
    constructor() {
        this.photoCount = 0;
        this.currentPhoto = null;
        this.photoHistory = [];
        this.maxHistorySize = 50; // Limite du nombre de photos en historique
    }

    /**
     * Sauvegarde une photo sur le serveur
     */
    async savePhotoToServer(imageBlob, filename = null) {
        if (!imageBlob) {
            throw new Error('Aucune image à sauvegarder');
        }

        try {
            console.log('Sauvegarde de la photo...');

            // Créer un FormData avec l'image
            const formData = new FormData();
            const photoFilename = filename || `photobooth_${Date.now()}.jpg`;
            formData.append('photo', imageBlob, photoFilename);

            // Envoyer la photo au serveur
            const response = await fetch('/upload/photo', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                console.log('Photo sauvegardée:', result);
                
                // Incrémenter le compteur
                this.photoCount++;
                
                // Ajouter à l'historique
                this.addToHistory(result);
                
                // Mettre à jour la photo courante
                this.currentPhoto = result;
                
                return result;
            } else {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

        } catch (error) {
            console.error('Erreur lors de la sauvegarde de la photo:', error);
            throw error;
        }
    }

    /**
     * Ajoute une photo à l'historique
     */
    addToHistory(photoData) {
        this.photoHistory.unshift({
            ...photoData,
            timestamp: new Date().toISOString()
        });

        // Limiter la taille de l'historique
        if (this.photoHistory.length > this.maxHistorySize) {
            this.photoHistory = this.photoHistory.slice(0, this.maxHistorySize);
        }
    }

    /**
     * Obtient l'historique des photos
     */
    getPhotoHistory() {
        return [...this.photoHistory];
    }

    /**
     * Obtient la photo courante
     */
    getCurrentPhoto() {
        return this.currentPhoto;
    }

    /**
     * Obtient le nombre total de photos
     */
    getPhotoCount() {
        return this.photoCount;
    }

    /**
     * Met à jour le compteur de photos
     */
    updatePhotoCount() {
        const countElement = document.getElementById('photo-count');
        if (countElement) {
            countElement.textContent = this.photoCount;
        }
    }

    /**
     * Télécharge une photo
     */
    downloadPhoto(imageBlob, filename = null) {
        if (!imageBlob) {
            throw new Error('Aucune image à télécharger');
        }

        try {
            const url = URL.createObjectURL(imageBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename || `photobooth_${Date.now()}.jpg`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            console.log('Photo téléchargée');
            return true;

        } catch (error) {
            console.error('Erreur lors du téléchargement:', error);
            throw error;
        }
    }

    /**
     * Supprime une photo du serveur
     */
    async deletePhoto(filename) {
        try {
            const response = await fetch(`/admin/photos/${filename}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                console.log('Photo supprimée:', filename);
                
                // Retirer de l'historique
                this.photoHistory = this.photoHistory.filter(photo => photo.filename !== filename);
                
                // Décrémenter le compteur si c'était la photo courante
                if (this.currentPhoto && this.currentPhoto.filename === filename) {
                    this.currentPhoto = null;
                }
                
                return true;
            } else {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

        } catch (error) {
            console.error('Erreur lors de la suppression de la photo:', error);
            throw error;
        }
    }

    /**
     * Obtient les métadonnées d'une photo
     */
    getPhotoMetadata(photoData) {
        return {
            filename: photoData.filename,
            size: photoData.size || 0,
            uploadTime: photoData.upload_time || new Date().toISOString(),
            dimensions: photoData.dimensions || null,
            format: photoData.format || 'unknown'
        };
    }

    /**
     * Formate la taille d'un fichier
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Formate une date
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('fr-FR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Vide l'historique des photos
     */
    clearHistory() {
        this.photoHistory = [];
        console.log('Historique des photos vidé');
    }

    /**
     * Exporte l'historique des photos
     */
    exportHistory() {
        try {
            const dataStr = JSON.stringify(this.photoHistory, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const url = URL.createObjectURL(dataBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `photobooth_history_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log('Historique exporté');
            return true;
        } catch (error) {
            console.error('Erreur lors de l\'export:', error);
            throw error;
        }
    }

    /**
     * Obtient les statistiques des photos
     */
    getPhotoStats() {
        const totalSize = this.photoHistory.reduce((sum, photo) => sum + (photo.size || 0), 0);
        const formats = this.photoHistory.reduce((acc, photo) => {
            const format = photo.format || 'unknown';
            acc[format] = (acc[format] || 0) + 1;
            return acc;
        }, {});

        return {
            totalPhotos: this.photoCount,
            totalSize: totalSize,
            formattedSize: this.formatFileSize(totalSize),
            formats: formats,
            averageSize: this.photoCount > 0 ? totalSize / this.photoCount : 0
        };
    }
}

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PhotoManager;
} else {
    // Export global pour utilisation dans le navigateur
    window.PhotoManager = PhotoManager;
}
