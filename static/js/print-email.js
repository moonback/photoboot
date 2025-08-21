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
        document.getElementById('print-photo').addEventListener('click', () => this.showPrintModal());
        document.getElementById('email-photo').addEventListener('click', () => this.showEmailModal());

        // Fermeture des modales
        document.getElementById('close-print').addEventListener('click', () => this.hidePrintModal());
        document.getElementById('close-email').addEventListener('click', () => this.hideEmailModal());

        // Actions
        document.getElementById('start-print').addEventListener('click', () => this.startPrint());
        document.getElementById('send-email').addEventListener('click', () => this.sendEmail());

        // Validation email
        document.getElementById('user-email').addEventListener('blur', (e) => this.validateEmail(e.target.value));

        // Consentement RGPD
        document.getElementById('gdpr-consent').addEventListener('change', (e) => this.handleGdprConsent(e.target.checked));
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
            console.error('Erreur lors du chargement des imprimantes:', error);
        }
    }

    updatePrinterSelect() {
        const select = document.getElementById('printer-select');
        select.innerHTML = '<option value="">Imprimante par défaut</option>';

        this.printers.forEach(printer => {
            const option = document.createElement('option');
            option.value = printer.name;
            option.textContent = `${printer.name} (${printer.platform})`;
            select.appendChild(option);
        });
    }

    async loadGdprConsent() {
        try {
            const response = await fetch('/email/gdpr-consent');
            if (response.ok) {
                this.gdprConsent = await response.json();
                this.updateGdprText();
            }
        } catch (error) {
            console.error('Erreur lors du chargement du consentement RGPD:', error);
        }
    }

    updateGdprText() {
        if (this.gdprConsent) {
            const gdprText = document.getElementById('gdpr-text');
            gdprText.textContent = this.gdprConsent.consent_text;
            gdprText.classList.remove('hidden');
        }
    }

    showPrintModal() {
        if (!this.currentPhotoPath) {
            this.showError('Aucune photo à imprimer');
            return;
        }

        document.getElementById('print-modal').classList.remove('hidden');
        this.hideStatus('print');
    }

    hidePrintModal() {
        document.getElementById('print-modal').classList.add('hidden');
    }

    showEmailModal() {
        if (!this.currentPhotoPath) {
            this.showError('Aucune photo à envoyer');
            return;
        }

        document.getElementById('email-modal').classList.remove('hidden');
        this.hideStatus('email');

        // Réinitialiser le formulaire
        document.getElementById('user-name').value = '';
        document.getElementById('user-email').value = '';
        document.getElementById('gdpr-consent').checked = false;
    }

    hideEmailModal() {
        document.getElementById('email-modal').classList.add('hidden');
    }

    async startPrint() {
        if (!this.currentPhotoPath) {
            this.showStatus('print', 'Erreur: Aucune photo sélectionnée', 'error');
            return;
        }

        const printerName = document.getElementById('printer-select').value;
        const copies = parseInt(document.getElementById('print-copies').value);
        const paperSize = document.getElementById('paper-size').value;

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

        const userName = document.getElementById('user-name').value.trim();
        const userEmail = document.getElementById('user-email').value.trim();
        const consentGiven = document.getElementById('gdpr-consent').checked;

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
            document.getElementById('gdpr-text').classList.remove('hidden');
        } else {
            document.getElementById('gdpr-text').classList.add('hidden');
        }
    }

    showStatus(type, message, status = 'info') {
        const statusElement = document.getElementById(`${type}-status`);
        statusElement.textContent = message;
        statusElement.className = `admin-status ${status}`;
        statusElement.classList.remove('hidden');
    }

    hideStatus(type) {
        const statusElement = document.getElementById(`${type}-status`);
        statusElement.classList.add('hidden');
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
