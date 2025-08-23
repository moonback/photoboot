/**
 * Gestion de l'impression et de l'email pour Photobooth
 */

class PrintEmailManager {
    constructor() {
        console.log('🔧 PrintEmailManager: Constructeur appelé');
        this.currentPhotoPath = null;
        this.currentPhotoUrl = null;
        this.printers = [];
        this.gdprConsent = null;

        this.initializeEventListeners();
        this.loadPrinters();
        this.loadGdprConsent();
        console.log('🔧 PrintEmailManager: Initialisation terminée');
    }

    initializeEventListeners() {
        // Boutons d'impression et email
        const printPhotoBtn = document.getElementById('print-photo');
        const emailPhotoBtn = document.getElementById('email-photo');
        
        if (printPhotoBtn) {
            printPhotoBtn.addEventListener('click', () => this.showPrintModal());
        }
        
        if (emailPhotoBtn) {
            emailPhotoBtn.addEventListener('click', () => this.showEmailModal());
        }

        // Fermeture des modales
        const closePrintBtn = document.getElementById('close-print');
        const closeEmailBtn = document.getElementById('close-email');
        
        if (closePrintBtn) {
            closePrintBtn.addEventListener('click', () => this.hidePrintModal());
        }
        
        if (closeEmailBtn) {
            closeEmailBtn.addEventListener('click', () => this.hideEmailModal());
        }

        // Actions
        const startPrintBtn = document.getElementById('start-print');
        const sendEmailBtn = document.getElementById('send-email');
        
        if (startPrintBtn) {
            startPrintBtn.addEventListener('click', () => this.startPrint());
        }
        
        if (sendEmailBtn) {
            sendEmailBtn.addEventListener('click', () => this.sendEmail());
        }

        // Validation email
        const userEmailInput = document.getElementById('user-email');
        if (userEmailInput) {
            userEmailInput.addEventListener('blur', (e) => this.validateEmail(e.target.value));
        }

        // Consentement RGPD
        const gdprConsentCheckbox = document.getElementById('gdpr-consent');
        if (gdprConsentCheckbox) {
            gdprConsentCheckbox.addEventListener('change', (e) => this.handleGdprConsent(e.target.checked));
        }
    }

    setCurrentPhoto(photoPath, photoUrl) {
        console.log('setCurrentPhoto appelé avec:', { photoPath, photoUrl });
        this.currentPhotoPath = photoPath;
        this.currentPhotoUrl = photoUrl;
        console.log('Photo définie:', { photoPath, photoUrl });
        console.log('this.currentPhotoPath après définition:', this.currentPhotoPath);
    }

    async loadPrinters() {
        try {
            const response = await fetch('/print/printers');
            if (response.ok) {
                const data = await response.json();
                this.printers = data.printers;
                this.updatePrinterSelect();
            }
        } catch (error) {
            console.log('API imprimantes non disponible, utilisation des valeurs par défaut');
            // Utiliser des valeurs par défaut si l'API n'est pas disponible
            this.printers = [
                { name: 'Imprimante par défaut', platform: 'Local' }
            ];
            this.updatePrinterSelect();
        }
    }

    updatePrinterSelect() {
        const select = document.getElementById('printer-select');
        if (select) {
            select.innerHTML = '<option value="">Imprimante par défaut</option>';

            this.printers.forEach(printer => {
                const option = document.createElement('option');
                option.value = printer.name;
                option.textContent = `${printer.name} (${printer.platform})`;
                select.appendChild(option);
            });
        }
    }

    async loadGdprConsent() {
        try {
            const response = await fetch('/email/gdpr-consent');
            if (response.ok) {
                this.gdprConsent = await response.json();
                this.updateGdprText();
            }
        } catch (error) {
            console.log('API RGPD non disponible, utilisation des valeurs par défaut');
            // Utiliser des valeurs par défaut si l'API n'est pas disponible
            this.gdprConsent = {
                required: true,
                consent_text: "J'accepte que mes données soient utilisées pour l'envoi de cette photo"
            };
        }
    }

    updateGdprText() {
        if (this.gdprConsent) {
            const gdprText = document.getElementById('gdpr-text');
            if (gdprText) {
                gdprText.textContent = this.gdprConsent.consent_text;
                gdprText.classList.remove('hidden');
            }
        }
    }

    showPrintModal() {
        if (!this.currentPhotoPath) {
            this.showError('Aucune photo à imprimer');
            return;
        }

        const printModal = document.getElementById('print-modal');
        if (printModal) {
            printModal.classList.remove('hidden');
            this.hideStatus('print');
        }
    }

    hidePrintModal() {
        const printModal = document.getElementById('print-modal');
        if (printModal) {
            printModal.classList.add('hidden');
        }
    }

    showEmailModal() {
        if (!this.currentPhotoPath) {
            this.showError('Aucune photo à envoyer');
            return;
        }

        const emailModal = document.getElementById('email-modal');
        if (emailModal) {
            emailModal.classList.remove('hidden');
            this.hideStatus('email');

            // Réinitialiser le formulaire
            const userNameInput = document.getElementById('user-name');
            const userEmailInput = document.getElementById('user-email');
            const gdprConsentCheckbox = document.getElementById('gdpr-consent');
            
            if (userNameInput) userNameInput.value = '';
            if (userEmailInput) userEmailInput.value = '';
            if (gdprConsentCheckbox) gdprConsentCheckbox.checked = false;
        }
    }

    hideEmailModal() {
        const emailModal = document.getElementById('email-modal');
        if (emailModal) {
            emailModal.classList.add('hidden');
        }
    }

    async startPrint() {
        if (!this.currentPhotoPath) {
            this.showStatus('print', 'Erreur: Aucune photo sélectionnée', 'error');
            return;
        }

        const printerSelect = document.getElementById('printer-select');
        const printCopies = document.getElementById('print-copies');
        const paperSize = document.getElementById('paper-size');
        
        if (!printerSelect || !printCopies || !paperSize) {
            this.showStatus('print', 'Erreur: Éléments d\'impression manquants', 'error');
            return;
        }

        const printerName = printerSelect.value;
        const copies = parseInt(printCopies.value);

        if (copies < 1 || copies > 10) {
            this.showStatus('print', 'Nombre de copies invalide', 'error');
            return;
        }

        this.showStatus('print', 'Impression en cours...', 'info');

        try {
            const response = await fetch('/print/photo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    photo_path: this.currentPhotoPath,
                    copies: copies,
                    printer_name: printerName || null
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showStatus('print', `Impression lancée avec succès sur ${result.printer || 'l\'imprimante par défaut'}`, 'success');
                setTimeout(() => this.hidePrintModal(), 3000);
            } else {
                this.showStatus('print', `Erreur d'impression: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors de l\'impression:', error);
            this.showStatus('print', 'Erreur de connexion au serveur', 'error');
        }
    }

    async sendEmail() {
        if (!this.currentPhotoPath) {
            this.showStatus('email', 'Erreur: Aucune photo sélectionnée', 'error');
            return;
        }

        const userNameInput = document.getElementById('user-name');
        const userEmailInput = document.getElementById('user-email');
        const gdprConsentCheckbox = document.getElementById('gdpr-consent');
        
        if (!userNameInput || !userEmailInput || !gdprConsentCheckbox) {
            this.showStatus('email', 'Erreur: Éléments du formulaire manquants', 'error');
            return;
        }

        const userName = userNameInput.value.trim();
        const userEmail = userEmailInput.value.trim();
        const consentGiven = gdprConsentCheckbox.checked;

        if (!userEmail) {
            this.showStatus('email', 'Adresse email requise', 'error');
            return;
        }

        if (!this.validateEmail(userEmail)) {
            this.showStatus('email', 'Format d\'email invalide', 'error');
            return;
        }

        if (this.gdprConsent?.required && !consentGiven) {
            this.showStatus('email', 'Consentement RGPD requis', 'error');
            return;
        }

        this.showStatus('email', 'Envoi en cours...', 'info');

        try {
            // Créer un lien de téléchargement temporaire
            const downloadLink = `${window.location.origin}/download/${encodeURIComponent(this.currentPhotoPath)}`;

            const response = await fetch('/email/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    to_email: userEmail,
                    photo_path: this.currentPhotoPath,
                    download_link: downloadLink,
                    consent_given: consentGiven,
                    user_name: userName
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showStatus('email', `Email envoyé avec succès à ${userEmail}`, 'success');
                setTimeout(() => this.hideEmailModal(), 3000);
            } else {
                this.showStatus('email', `Erreur d'envoi: ${result.error}`, 'error');
            }
        } catch (error) {
            console.error('Erreur lors de l\'envoi de l\'email:', error);
            this.showStatus('email', 'Erreur de connexion au serveur', 'error');
        }
    }

    validateEmail(email) {
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return emailPattern.test(email);
    }

    handleGdprConsent(checked) {
        if (checked && this.gdprConsent?.required) {
            const gdprText = document.getElementById('gdpr-text');
            if (gdprText) {
                gdprText.classList.remove('hidden');
            }
        } else {
            const gdprText = document.getElementById('gdpr-text');
            if (gdprText) {
                gdprText.classList.add('hidden');
            }
        }
    }

    showStatus(type, message, status = 'info') {
        const statusElement = document.getElementById(`${type}-status`);
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `admin-status ${status}`;
            statusElement.classList.remove('hidden');
        }
    }

    hideStatus(type) {
        const statusElement = document.getElementById(`${type}-status`);
        if (statusElement) {
            statusElement.classList.add('hidden');
        }
    }

    showError(message) {
        // Utiliser une alerte simple pour l'instant
        alert(message);
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', function () {
    window.printEmailManager = new PrintEmailManager();
});
