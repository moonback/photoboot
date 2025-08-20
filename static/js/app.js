/**
 * Application JavaScript principale du photobooth
 * Gère l'interface utilisateur et les interactions
 */

class PhotoboothApp {
    constructor() {
        this.currentMode = 'single'; // 'single' ou 'multi'
        this.currentFilter = 'none';
        this.currentTemplate = 'strip_2x6';
        this.capturedPhotos = [];
        this.photoCount = 0;
        this.isCapturing = false;
        this.stream = null;
        this.countdownInterval = null;

        this.init();
    }

    init() {
        this.bindEvents();
        this.updateStatus();
        this.loadPhotoCount();
    }

    bindEvents() {
        // Boutons de mode de capture
        document.getElementById('single-mode').addEventListener('click', () => this.setMode('single'));
        document.getElementById('multi-mode').addEventListener('click', () => this.setMode('multi'));

        // Boutons de filtre
        document.getElementById('filter-none').addEventListener('click', () => this.setFilter('none'));
        document.getElementById('filter-vintage').addEventListener('click', () => this.setFilter('vintage'));
        document.getElementById('filter-bw').addEventListener('click', () => this.setFilter('bw'));
        document.getElementById('filter-warm').addEventListener('click', () => this.setFilter('warm'));

        // Boutons de template
        document.getElementById('template-strip').addEventListener('click', () => this.setTemplate('strip_2x6'));
        document.getElementById('template-postcard').addEventListener('click', () => this.setTemplate('postcard_4x6'));

        // Bouton principal
        document.getElementById('start-button').addEventListener('click', () => this.startCapture());

        // Boutons de contrôle
        document.getElementById('cancel-capture').addEventListener('click', () => this.cancelCapture());
        document.getElementById('retake-photos').addEventListener('click', () => this.retakePhotos());
        document.getElementById('validate-photos').addEventListener('click', () => this.validatePhotos());
        document.getElementById('back-to-results').addEventListener('click', () => this.showResults());
        document.getElementById('generate-print').addEventListener('click', () => this.generatePrint());

        // Bouton admin
        document.getElementById('admin-button').addEventListener('click', () => this.showAdminModal());
        document.getElementById('close-admin').addEventListener('click', () => this.hideAdminModal());
        document.getElementById('admin-login').addEventListener('click', () => this.adminLogin());

        // Gestion des touches clavier
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
    }

    setMode(mode) {
        this.currentMode = mode;

        // Mettre à jour l'interface
        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`${mode}-mode`).classList.add('active');

        // Mettre à jour le texte du bouton principal
        const startBtn = document.getElementById('start-button');
        if (mode === 'multi') {
            startBtn.querySelector('.btn-text').textContent = 'CAPTURER 4 PHOTOS';
        } else {
            startBtn.querySelector('.btn-text').textContent = 'DÉMARRER';
        }
    }

    setFilter(filter) {
        this.currentFilter = filter;

        // Mettre à jour l'interface
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`filter-${filter}`).classList.add('active');
    }

    setTemplate(template) {
        this.currentTemplate = template;

        // Mettre à jour l'interface
        document.querySelectorAll('.template-btn').forEach(btn => btn.classList.remove('active'));

        // Mapper les templates aux IDs des boutons
        let buttonId;
        if (template === 'strip_2x6') {
            buttonId = 'template-strip';
        } else if (template === 'postcard_4x6') {
            buttonId = 'template-postcard';
        } else {
            buttonId = `template-${template.replace('_', '-')}`;
        }

        const button = document.getElementById(buttonId);
        if (button) {
            button.classList.add('active');
        }
    }

    async startCapture() {
        if (this.isCapturing) return;

        try {
            // Démarrer la caméra
            await this.startCamera();

            // Afficher l'interface de capture
            this.showInterface('capture');

            // Démarrer le compte à rebours
            this.startCountdown();

        } catch (error) {
            console.error('Erreur lors du démarrage de la capture:', error);
            this.showError('Impossible de démarrer la caméra');
        }
    }

    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: 'user'
                }
            });

            const video = document.getElementById('camera-video');
            video.srcObject = this.stream;

            // Mettre à jour le statut de la caméra
            document.getElementById('camera-status').className = 'status-indicator bg-green-500';
            document.getElementById('camera-status').querySelector('.status-text').textContent = 'Caméra';

        } catch (error) {
            throw new Error('Accès à la caméra refusé');
        }
    }

    startCountdown() {
        let count = 3;
        const countdownElement = document.getElementById('countdown-number');
        const multiProgress = document.getElementById('multi-progress');

        // Afficher/masquer la progression selon le mode
        if (this.currentMode === 'multi') {
            multiProgress.classList.remove('hidden');
            this.updateMultiProgress(1, this.currentMode === 'multi' ? 4 : 1);
        } else {
            multiProgress.classList.add('hidden');
        }

        countdownElement.textContent = count;

        this.countdownInterval = setInterval(() => {
            count--;
            countdownElement.textContent = count;

            if (count <= 0) {
                clearInterval(this.countdownInterval);
                this.capturePhoto();
            }
        }, 1000);
    }

    async capturePhoto() {
        try {
            const video = document.getElementById('camera-video');
            const canvas = document.getElementById('capture-canvas');
            const context = canvas.getContext('2d');

            // Configurer le canvas
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            // Capturer la frame
            context.drawImage(video, 0, 0);

            // Appliquer le filtre
            this.applyFilter(context, canvas.width, canvas.height);

            // Convertir en blob
            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9));

            // Créer l'URL de la photo
            const photoUrl = URL.createObjectURL(blob);

            // Ajouter à la liste des photos capturées
            this.capturedPhotos.push({
                url: photoUrl,
                blob: blob,
                timestamp: Date.now()
            });

            // Mettre à jour le compteur
            this.photoCount++;
            this.updatePhotoCount();

            // Vérifier si on continue ou si on a fini
            if (this.currentMode === 'multi' && this.capturedPhotos.length < 4) {
                // Continuer avec la photo suivante
                this.updateMultiProgress(this.capturedPhotos.length + 1, 4);
                setTimeout(() => this.startCountdown(), 1000);
            } else {
                // Fin de la capture
                this.stopCamera();
                this.showResults();
            }

        } catch (error) {
            console.error('Erreur lors de la capture:', error);
            this.showError('Erreur lors de la capture');
        }
    }

    applyFilter(context, width, height) {
        const imageData = context.getImageData(0, 0, width, height);
        const data = imageData.data;

        switch (this.currentFilter) {
            case 'vintage':
                // Filtre vintage (sépia)
                for (let i = 0; i < data.length; i += 4) {
                    const r = data[i];
                    const g = data[i + 1];
                    const b = data[i + 2];

                    data[i] = Math.min(255, (r * 0.393) + (g * 0.769) + (b * 0.189));
                    data[i + 1] = Math.min(255, (r * 0.349) + (g * 0.686) + (b * 0.168));
                    data[i + 2] = Math.min(255, (r * 0.272) + (g * 0.534) + (b * 0.131));
                }
                break;

            case 'bw':
                // Filtre noir et blanc
                for (let i = 0; i < data.length; i += 4) {
                    const gray = (data[i] * 0.299) + (data[i + 1] * 0.587) + (data[i + 2] * 0.114);
                    data[i] = gray;
                    data[i + 1] = gray;
                    data[i + 2] = gray;
                }
                break;

            case 'warm':
                // Filtre chaud
                for (let i = 0; i < data.length; i += 4) {
                    data[i] = Math.min(255, data[i] * 1.1);     // Rouge augmenté
                    data[i + 1] = Math.min(255, data[i + 1] * 1.05); // Vert légèrement augmenté
                    data[i + 2] = Math.min(255, data[i + 2] * 0.9);  // Bleu diminué
                }
                break;
        }

        context.putImageData(imageData, 0, 0);
    }

    updateMultiProgress(current, total) {
        document.getElementById('current-photo').textContent = current;
        document.getElementById('total-photos').textContent = total;

        const progress = (current / total) * 100;
        document.getElementById('progress-bar').style.width = `${progress}%`;
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        // Mettre à jour le statut de la caméra
        document.getElementById('camera-status').className = 'status-indicator bg-red-500';
        document.getElementById('camera-status').querySelector('.status-text').textContent = 'Caméra';
    }

    cancelCapture() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
        }

        this.stopCamera();
        this.capturedPhotos = [];
        this.showInterface('main');
    }

    showResults() {
        this.showInterface('result');
        this.displayCapturedPhotos();
    }

    displayCapturedPhotos() {
        const grid = document.getElementById('photos-grid');
        grid.innerHTML = '';

        // Définir la classe CSS selon le nombre de photos
        grid.className = `photos-grid ${this.currentMode}`;

        this.capturedPhotos.forEach((photo, index) => {
            const photoItem = document.createElement('div');
            photoItem.className = 'photo-item fade-in-up';
            photoItem.style.animationDelay = `${index * 0.1}s`;

            photoItem.innerHTML = `
                <img src="${photo.url}" alt="Photo ${index + 1}">
                <div class="photo-number">${index + 1}</div>
            `;

            grid.appendChild(photoItem);
        });
    }

    retakePhotos() {
        this.capturedPhotos.forEach(photo => URL.revokeObjectURL(photo.url));
        this.capturedPhotos = [];
        this.showInterface('main');
    }

    validatePhotos() {
        this.showInterface('composition');
        this.updateCompositionPreview();
    }

    updateCompositionPreview() {
        const container = document.getElementById('preview-container');

        if (this.capturedPhotos.length === 0) {
            container.innerHTML = '<p class="text-gray-500">Aucune photo à afficher</p>';
            return;
        }

        // Créer un aperçu simple de la composition
        const preview = document.createElement('div');
        preview.className = 'text-center';

        const template = this.currentTemplate;
        if (template === 'strip_2x6') {
            preview.innerHTML = `
                <div class="bg-gray-200 p-4 rounded-lg inline-block">
                    <div class="flex space-x-2">
                        ${this.capturedPhotos.slice(0, 2).map((_, i) =>
                `<div class="w-16 h-12 bg-blue-300 rounded"></div>`
            ).join('')}
                    </div>
                    <p class="text-sm text-gray-600 mt-2">Bande 2x6</p>
                </div>
            `;
        } else {
            preview.innerHTML = `
                <div class="bg-gray-200 p-4 rounded-lg inline-block">
                    <div class="w-24 h-32 bg-blue-300 rounded"></div>
                    <p class="text-sm text-gray-600 mt-2">Carte 4x6</p>
                </div>
            `;
        }

        container.innerHTML = '';
        container.appendChild(preview);
    }

    async generatePrint() {
        try {
            const customText = document.getElementById('custom-text').value.trim();

            // Préparer les données pour l'API
            const formData = new FormData();
            formData.append('template', this.currentTemplate);
            if (customText) {
                formData.append('text_overlay', customText);
            }

            // Ajouter les photos
            this.capturedPhotos.forEach((photo, index) => {
                formData.append('photos', photo.blob, `photo_${index + 1}.jpg`);
            });

            // Envoyer à l'API de composition
            const response = await fetch('/api/compose', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.showSuccess('Composition générée avec succès !');

                // Télécharger le fichier final
                setTimeout(() => {
                    this.downloadFile(result.canvas_path, `photobooth_${this.currentTemplate}.png`);
                }, 1000);

            } else {
                throw new Error('Erreur lors de la génération');
            }

        } catch (error) {
            console.error('Erreur lors de la génération:', error);
            this.showError('Erreur lors de la génération de la composition');
        }
    }

    downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    showInterface(interfaceName) {
        // Masquer toutes les interfaces
        const interfaces = ['main', 'capture', 'result', 'composition'];
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
            targetInterface.classList.add('fade-in-up');
        }
    }

    updatePhotoCount() {
        document.getElementById('photo-count').textContent = this.photoCount;

        // Sauvegarder dans le localStorage
        localStorage.setItem('photobooth_photo_count', this.photoCount.toString());
    }

    loadPhotoCount() {
        const saved = localStorage.getItem('photobooth_photo_count');
        if (saved) {
            this.photoCount = parseInt(saved);
            this.updatePhotoCount();
        }
    }

    updateStatus() {
        // Vérifier le statut du stockage
        const storageStatus = document.getElementById('storage-status');
        if (navigator.storage && navigator.storage.estimate) {
            navigator.storage.estimate().then(estimate => {
                const usagePercent = (estimate.usage / estimate.quota) * 100;
                if (usagePercent > 90) {
                    storageStatus.className = 'status-indicator bg-red-500';
                    storageStatus.querySelector('.status-text').textContent = 'Stockage plein';
                } else if (usagePercent > 70) {
                    storageStatus.className = 'status-indicator bg-yellow-500';
                    storageStatus.querySelector('.status-text').textContent = 'Stockage limité';
                }
            });
        }
    }

    showAdminModal() {
        document.getElementById('admin-modal').classList.remove('hidden');
    }

    hideAdminModal() {
        document.getElementById('admin-modal').classList.add('hidden');
    }

    async adminLogin() {
        const username = document.getElementById('admin-username').value;
        const password = document.getElementById('admin-password').value;
        const statusElement = document.getElementById('admin-status');

        try {
            const response = await fetch('/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (response.ok) {
                statusElement.textContent = 'Connexion réussie !';
                statusElement.className = 'admin-status success';
                setTimeout(() => {
                    window.location.href = '/admin';
                }, 1000);
            } else {
                throw new Error('Identifiants invalides');
            }

        } catch (error) {
            statusElement.textContent = 'Erreur de connexion';
            statusElement.className = 'admin-status error';
        }

        statusElement.classList.remove('hidden');
    }

    handleKeyPress(event) {
        switch (event.key) {
            case 'Escape':
                if (this.isCapturing) {
                    this.cancelCapture();
                }
                break;
            case ' ':
                if (!this.isCapturing) {
                    event.preventDefault();
                    this.startCapture();
                }
                break;
        }
    }

    showError(message) {
        // Implémenter l'affichage d'erreur
        console.error(message);
    }

    showSuccess(message) {
        // Implémenter l'affichage de succès
        console.log(message);
    }
}

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', () => {
    window.photoboothApp = new PhotoboothApp();
});
