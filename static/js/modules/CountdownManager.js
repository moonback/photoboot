/**
 * Module de gestion du compte à rebours pour le photobooth
 * Responsable de l'animation et du timing du compte à rebours
 */
class CountdownManager {
    constructor() {
        this.countdownInterval = null;
        this.currentCount = 0;
        this.totalCount = 3;
        this.isRunning = false;
        this.onComplete = null;
        this.onTick = null;
        this.countdownElement = null;
    }

    /**
     * Initialise le gestionnaire de compte à rebours
     */
    init(countdownElement, onComplete = null, onTick = null) {
        this.countdownElement = countdownElement;
        this.onComplete = onComplete;
        this.onTick = onTick;
        console.log('Gestionnaire de compte à rebours initialisé');
    }

    /**
     * Démarre le compte à rebours
     */
    startCountdown(count = 3) {
        if (this.isRunning) {
            console.log('Compte à rebours déjà en cours');
            return;
        }

        this.totalCount = count;
        this.currentCount = count;
        this.isRunning = true;

        console.log(`Démarrage du compte à rebours: ${count} secondes`);

        // Afficher le premier nombre
        this.updateDisplay();

        // Démarrer l'intervalle
        this.countdownInterval = setInterval(() => {
            this.currentCount--;

            // Appeler le callback de tick si défini
            if (this.onTick) {
                this.onTick(this.currentCount);
            }

            // Mettre à jour l'affichage
            this.updateDisplay();

            // Vérifier si le compte à rebours est terminé
            if (this.currentCount <= 0) {
                this.stopCountdown();
                
                // Appeler le callback de fin si défini
                if (this.onComplete) {
                    this.onComplete();
                }
            }
        }, 1000);
    }

    /**
     * Arrête le compte à rebours
     */
    stopCountdown() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }

        this.isRunning = false;
        this.currentCount = 0;

        console.log('Compte à rebours arrêté');
    }

    /**
     * Met en pause le compte à rebours
     */
    pauseCountdown() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
        console.log('Compte à rebours mis en pause');
    }

    /**
     * Reprend le compte à rebours
     */
    resumeCountdown() {
        if (!this.isRunning || this.currentCount <= 0) {
            console.log('Impossible de reprendre le compte à rebours');
            return;
        }

        this.countdownInterval = setInterval(() => {
            this.currentCount--;

            if (this.onTick) {
                this.onTick(this.currentCount);
            }

            this.updateDisplay();

            if (this.currentCount <= 0) {
                this.stopCountdown();
                if (this.onComplete) {
                    this.onComplete();
                }
            }
        }, 1000);

        console.log('Compte à rebours repris');
    }

    /**
     * Met à jour l'affichage du compte à rebours
     */
    updateDisplay() {
        if (this.countdownElement) {
            this.countdownElement.textContent = this.currentCount;
            
            // Ajouter une classe pour l'animation
            this.countdownElement.classList.add('countdown-active');
            
            // Retirer la classe après l'animation
            setTimeout(() => {
                this.countdownElement.classList.remove('countdown-active');
            }, 200);
        }
    }

    /**
     * Change la durée du compte à rebours
     */
    setCountdownDuration(seconds) {
        if (this.isRunning) {
            console.log('Impossible de changer la durée pendant le compte à rebours');
            return;
        }

        this.totalCount = Math.max(1, Math.min(10, seconds)); // Limiter entre 1 et 10 secondes
        console.log(`Durée du compte à rebours changée à ${this.totalCount} secondes`);
    }

    /**
     * Obtient le statut du compte à rebours
     */
    getStatus() {
        return {
            isRunning: this.isRunning,
            currentCount: this.currentCount,
            totalCount: this.totalCount,
            remainingTime: Math.max(0, this.currentCount),
            progress: this.totalCount > 0 ? ((this.totalCount - this.currentCount) / this.totalCount) * 100 : 0
        };
    }

    /**
     * Obtient le temps restant en secondes
     */
    getRemainingTime() {
        return Math.max(0, this.currentCount);
    }

    /**
     * Obtient le pourcentage de progression
     */
    getProgress() {
        if (this.totalCount <= 0) return 0;
        return ((this.totalCount - this.currentCount) / this.totalCount) * 100;
    }

    /**
     * Vérifie si le compte à rebours est terminé
     */
    isComplete() {
        return this.currentCount <= 0;
    }

    /**
     * Vérifie si le compte à rebours est en cours
     */
    isActive() {
        return this.isRunning;
    }

    /**
     * Réinitialise le compte à rebours
     */
    reset() {
        this.stopCountdown();
        this.currentCount = this.totalCount;
        this.updateDisplay();
        console.log('Compte à rebours réinitialisé');
    }

    /**
     * Ajoute des effets visuels au compte à rebours
     */
    addVisualEffects() {
        if (!this.countdownElement) return;

        // Ajouter des classes CSS pour les animations
        this.countdownElement.classList.add('countdown-enhanced');
        
        // Ajouter un effet de pulsation
        this.countdownElement.style.animation = 'countdown-pulse 1s ease-in-out';
    }

    /**
     * Supprime les effets visuels
     */
    removeVisualEffects() {
        if (!this.countdownElement) return;

        this.countdownElement.classList.remove('countdown-enhanced');
        this.countdownElement.style.animation = '';
    }

    /**
     * Obtient le temps écoulé depuis le début
     */
    getElapsedTime() {
        return this.totalCount - this.currentCount;
    }

    /**
     * Obtient le temps total du compte à rebours
     */
    getTotalTime() {
        return this.totalCount;
    }
}

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CountdownManager;
} else {
    // Export global pour utilisation dans le navigateur
    window.CountdownManager = CountdownManager;
}
