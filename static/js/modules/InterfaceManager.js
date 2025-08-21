/**
 * Module de gestion des interfaces utilisateur pour le photobooth
 * Responsable de la navigation entre les différentes interfaces
 */
class InterfaceManager {
    constructor() {
        this.currentInterface = 'main';
        this.interfaces = ['main', 'capture', 'result'];
        this.interfaceElements = new Map();
        this.transitionDuration = 500; // Durée de transition en ms
        this.isTransitioning = false;
    }

    /**
     * Initialise le gestionnaire d'interfaces
     */
    init() {
        // Récupérer tous les éléments d'interface
        this.interfaces.forEach(interfaceName => {
            const element = document.getElementById(`${interfaceName}-interface`);
            if (element) {
                this.interfaceElements.set(interfaceName, element);
            }
        });

        console.log('Gestionnaire d\'interfaces initialisé');
        this.showInterface('main'); // Afficher l'interface principale par défaut
    }

    /**
     * Affiche une interface spécifique
     */
    showInterface(interfaceName) {
        if (this.isTransitioning) {
            console.log('Transition en cours, veuillez patienter');
            return;
        }

        if (!this.interfaces.includes(interfaceName)) {
            console.error(`Interface inconnue: ${interfaceName}`);
            return;
        }

        if (this.currentInterface === interfaceName) {
            console.log(`Interface ${interfaceName} déjà affichée`);
            return;
        }

        console.log(`Transition vers l'interface: ${interfaceName}`);
        this.isTransitioning = true;

        // Masquer l'interface actuelle
        this.hideCurrentInterface();

        // Afficher la nouvelle interface
        this.displayInterface(interfaceName);

        // Mettre à jour l'état
        this.currentInterface = interfaceName;

        // Terminer la transition
        setTimeout(() => {
            this.isTransitioning = false;
        }, this.transitionDuration);
    }

    /**
     * Masque l'interface actuelle
     */
    hideCurrentInterface() {
        const currentElement = this.interfaceElements.get(this.currentInterface);
        if (currentElement) {
            currentElement.classList.add('hidden');
            currentElement.classList.remove('fade-in');
            currentElement.classList.add('fade-out');
        }
    }

    /**
     * Affiche une interface
     */
    displayInterface(interfaceName) {
        const targetElement = this.interfaceElements.get(interfaceName);
        if (targetElement) {
            targetElement.classList.remove('hidden');
            targetElement.classList.remove('fade-out');
            targetElement.classList.add('fade-in');
        }
    }

    /**
     * Masque toutes les interfaces
     */
    hideAllInterfaces() {
        this.interfaces.forEach(interfaceName => {
            const element = this.interfaceElements.get(interfaceName);
            if (element) {
                element.classList.add('hidden');
                element.classList.remove('fade-in', 'fade-out');
            }
        });
    }

    /**
     * Obtient l'interface actuelle
     */
    getCurrentInterface() {
        return this.currentInterface;
    }

    /**
     * Vérifie si une interface est affichée
     */
    isInterfaceVisible(interfaceName) {
        const element = this.interfaceElements.get(interfaceName);
        return element && !element.classList.contains('hidden');
    }

    /**
     * Obtient l'élément d'une interface
     */
    getInterfaceElement(interfaceName) {
        return this.interfaceElements.get(interfaceName);
    }

    /**
     * Ajoute une classe CSS à une interface
     */
    addClassToInterface(interfaceName, className) {
        const element = this.interfaceElements.get(interfaceName);
        if (element) {
            element.classList.add(className);
        }
    }

    /**
     * Supprime une classe CSS d'une interface
     */
    removeClassFromInterface(interfaceName, className) {
        const element = this.interfaceElements.get(interfaceName);
        if (element) {
            element.classList.remove(className);
        }
    }

    /**
     * Change la durée de transition
     */
    setTransitionDuration(duration) {
        this.transitionDuration = Math.max(100, Math.min(2000, duration));
        console.log(`Durée de transition changée à ${this.transitionDuration}ms`);
    }

    /**
     * Ajoute une nouvelle interface
     */
    addInterface(interfaceName, elementId) {
        if (this.interfaces.includes(interfaceName)) {
            console.warn(`Interface ${interfaceName} existe déjà`);
            return false;
        }

        const element = document.getElementById(elementId);
        if (!element) {
            console.error(`Élément ${elementId} non trouvé`);
            return false;
        }

        this.interfaces.push(interfaceName);
        this.interfaceElements.set(interfaceName, element);
        console.log(`Interface ${interfaceName} ajoutée`);
        return true;
    }

    /**
     * Supprime une interface
     */
    removeInterface(interfaceName) {
        if (interfaceName === 'main') {
            console.error('Impossible de supprimer l\'interface principale');
            return false;
        }

        if (this.currentInterface === interfaceName) {
            this.showInterface('main'); // Basculer vers l'interface principale
        }

        this.interfaces = this.interfaces.filter(name => name !== interfaceName);
        this.interfaceElements.delete(interfaceName);
        console.log(`Interface ${interfaceName} supprimée`);
        return true;
    }

    /**
     * Obtient la liste des interfaces disponibles
     */
    getAvailableInterfaces() {
        return [...this.interfaces];
    }

    /**
     * Vérifie si une transition est en cours
     */
    isTransitionInProgress() {
        return this.isTransitioning;
    }

    /**
     * Force l'affichage d'une interface (sans transition)
     */
    forceShowInterface(interfaceName) {
        if (!this.interfaces.includes(interfaceName)) {
            console.error(`Interface inconnue: ${interfaceName}`);
            return;
        }

        this.hideAllInterfaces();
        this.displayInterface(interfaceName);
        this.currentInterface = interfaceName;
        console.log(`Interface ${interfaceName} affichée de force`);
    }

    /**
     * Ajoute des effets visuels à une interface
     */
    addVisualEffects(interfaceName, effects = []) {
        const element = this.interfaceElements.get(interfaceName);
        if (!element) return;

        effects.forEach(effect => {
            element.classList.add(`effect-${effect}`);
        });
    }

    /**
     * Supprime les effets visuels d'une interface
     */
    removeVisualEffects(interfaceName) {
        const element = this.interfaceElements.get(interfaceName);
        if (!element) return;

        // Supprimer toutes les classes d'effet
        element.classList.forEach(className => {
            if (className.startsWith('effect-')) {
                element.classList.remove(className);
            }
        });
    }

    /**
     * Obtient le statut des interfaces
     */
    getInterfaceStatus() {
        const status = {};
        this.interfaces.forEach(interfaceName => {
            status[interfaceName] = {
                isVisible: this.isInterfaceVisible(interfaceName),
                isCurrent: this.currentInterface === interfaceName,
                element: this.interfaceElements.has(interfaceName)
            };
        });
        return status;
    }

    /**
     * Réinitialise toutes les interfaces
     */
    reset() {
        this.hideAllInterfaces();
        this.currentInterface = 'main';
        this.isTransitioning = false;
        this.showInterface('main');
        console.log('Interfaces réinitialisées');
    }
}

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InterfaceManager;
} else {
    // Export global pour utilisation dans le navigateur
    window.InterfaceManager = InterfaceManager;
}
