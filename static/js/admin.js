// Application JavaScript pour l'interface d'administration du photobooth

class AdminApp {
    constructor() {
        this.currentSection = 'dashboard';
        this.adminInfo = null;
        this.refreshInterval = null;

        this.init();
    }

    init() {
        this.checkAuth();
        this.bindEvents();
        this.loadDashboard();
        this.startAutoRefresh();

        console.log('Interface d\'administration initialisée');
    }

    async checkAuth() {
        try {
            const response = await fetch('/admin/me');
            if (response.ok) {
                const data = await response.json();
                this.adminInfo = data;
                this.updateAdminInfo();
                this.loadCurrentSection();
            } else {
                // Rediriger vers la page de connexion si non authentifié
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Erreur de vérification d\'authentification:', error);
            window.location.href = '/';
        }
    }

    updateAdminInfo() {
        const usernameElement = document.getElementById('admin-username');
        if (usernameElement && this.adminInfo) {
            usernameElement.textContent = this.adminInfo.username;
        }
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.target.dataset.section;
                this.showSection(section);
            });
        });

        // Déconnexion
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Actions rapides
        const restartBtn = document.getElementById('restart-system');
        if (restartBtn) {
            restartBtn.addEventListener('click', () => this.restartSystem());
        }

        const backupBtn = document.getElementById('backup-system');
        if (backupBtn) {
            backupBtn.addEventListener('click', () => this.backupSystem());
        }

        const clearCacheBtn = document.getElementById('clear-cache');
        if (clearCacheBtn) {
            clearCacheBtn.addEventListener('click', () => this.clearCache());
        }

        const exportLogsBtn = document.getElementById('export-logs');
        if (exportLogsBtn) {
            exportLogsBtn.addEventListener('click', () => this.exportLogs());
        }

        // Formulaires
        const systemConfigForm = document.getElementById('system-config-form');
        if (systemConfigForm) {
            systemConfigForm.addEventListener('submit', (e) => this.saveSystemConfig(e));
        }

        const securityConfigForm = document.getElementById('security-config-form');
        if (securityConfigForm) {
            securityConfigForm.addEventListener('submit', (e) => this.saveSecurityConfig(e));
        }

        // Gestion des photos
        const refreshPhotosBtn = document.getElementById('refresh-photos');
        if (refreshPhotosBtn) {
            refreshPhotosBtn.addEventListener('click', () => this.loadPhotos());
        }

        const photoSearch = document.getElementById('photo-search');
        if (photoSearch) {
            photoSearch.addEventListener('input', (e) => this.searchPhotos(e.target.value));
        }

        // Sessions
        const terminateAllSessionsBtn = document.getElementById('terminate-all-sessions');
        if (terminateAllSessionsBtn) {
            terminateAllSessionsBtn.addEventListener('click', () => this.terminateAllSessions());
        }

        // Logs
        const clearLogsBtn = document.getElementById('clear-logs');
        if (clearLogsBtn) {
            clearLogsBtn.addEventListener('click', () => this.clearLogs());
        }

        const logLevelSelect = document.getElementById('log-level');
        if (logLevelSelect) {
            logLevelSelect.addEventListener('change', (e) => this.filterLogs(e.target.value));
        }
    }

    showSection(sectionName) {
        // Masquer toutes les sections
        document.querySelectorAll('.admin-section').forEach(section => {
            section.classList.add('hidden');
        });

        // Désactiver tous les boutons de navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });

        // Afficher la section demandée
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.remove('hidden');
        }

        // Activer le bouton de navigation correspondant
        const activeNavItem = document.querySelector(`[data-section="${sectionName}"]`);
        if (activeNavItem) {
            activeNavItem.classList.add('active');
        }

        this.currentSection = sectionName;
        this.loadCurrentSection();
    }

    loadCurrentSection() {
        switch (this.currentSection) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'photos':
                this.loadPhotos();
                break;
            case 'system':
                this.loadSystemConfig();
                break;
            case 'users':
                this.loadSessions();
                break;
            case 'logs':
                this.loadLogs();
                break;
        }
    }

    async loadDashboard() {
        try {
            // Charger les statistiques
            await this.loadStats();

            // Charger l'activité récente
            await this.loadRecentActivity();

        } catch (error) {
            console.error('Erreur lors du chargement du tableau de bord:', error);
        }
    }

    async loadStats() {
        try {
            // Statistiques des photos
            const photosResponse = await fetch('/admin/photos/count');
            if (photosResponse.ok) {
                const photosData = await photosResponse.json();
                this.updateStat('total-photos', photosData.count || 0);
            }

            // Sessions actives
            const sessionsResponse = await fetch('/admin/sessions');
            if (sessionsResponse.ok) {
                const sessionsData = await sessionsResponse.json();
                this.updateStat('active-sessions', sessionsData.total_sessions || 0);
            }

            // Statut système
            const healthResponse = await fetch('/health');
            if (healthResponse.ok) {
                const healthData = await healthResponse.json();
                this.updateStat('system-status', healthData.status === 'healthy' ? 'OK' : 'ERREUR');
            }

            // Espace disque (simulation)
            this.updateStat('disk-usage', '2.1 GB');

        } catch (error) {
            console.error('Erreur lors du chargement des statistiques:', error);
        }
    }

    updateStat(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    async loadRecentActivity() {
        try {
            const response = await fetch('/admin/activity');
            const activity = await response.json();

            const container = document.getElementById('recent-activity');
            if (container) {
                if (activity.activities && activity.activities.length > 0) {
                    container.innerHTML = activity.activities.map(item => `
                        <div class="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                            <div class="flex items-center space-x-3">
                                <span class="text-2xl">${item.icon}</span>
                                <div>
                                    <p class="font-medium">${item.action}</p>
                                    <p class="text-sm text-gray-400">${item.description}</p>
                                </div>
                            </div>
                            <span class="text-sm text-gray-500">${item.timestamp}</span>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = `
                        <div class="text-gray-400 text-center py-8">
                            Aucune activité récente
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Erreur lors du chargement de l\'activité:', error);
            const container = document.getElementById('recent-activity');
            if (container) {
                container.innerHTML = `
                    <div class="text-red-400 text-center py-8">
                        Erreur lors du chargement de l'activité
                    </div>
                `;
            }
        }
    }

    async loadPhotos() {
        try {
            const response = await fetch('/admin/photos');
            const photos = await response.json();

            const container = document.getElementById('photos-grid');
            if (container) {
                if (photos.photos && photos.photos.length > 0) {
                    container.innerHTML = photos.photos.map(photo => `
                        <div class="photo-item bg-gray-800 rounded-lg overflow-hidden">
                            <img src="/uploads/${photo.filename}" alt="Photo" class="w-full h-32 object-cover">
                            <div class="p-3">
                                <p class="text-sm font-medium truncate">${photo.filename}</p>
                                <p class="text-xs text-gray-400">${photo.size} - ${photo.date}</p>
                                <div class="flex space-x-2 mt-2">
                                    <button class="text-xs bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded" onclick="adminApp.downloadPhoto('${photo.filename}')">
                                        💾
                                    </button>
                                    <button class="text-xs bg-red-600 hover:bg-red-700 px-2 py-1 rounded" onclick="adminApp.deletePhoto('${photo.filename}')">
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = `
                        <div class="text-gray-400 text-center py-8">
                            Aucune photo trouvée
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Erreur lors du chargement des photos:', error);
        }
    }

    async loadSystemConfig() {
        try {
            const response = await fetch('/config');
            const config = await response.json();

            // Remplir le formulaire de configuration système
            const appName = document.getElementById('app-name');
            const appVersion = document.getElementById('app-version');
            const debugMode = document.getElementById('debug-mode');

            if (appName) appName.value = config.app?.name || '';
            if (appVersion) appVersion.value = config.app?.version || '';
            if (debugMode) debugMode.value = config.app?.debug?.toString() || 'false';

            // Remplir le formulaire de sécurité
            const sessionTimeout = document.getElementById('session-timeout');
            const bcryptRounds = document.getElementById('bcrypt-rounds');

            if (sessionTimeout) sessionTimeout.value = config.security?.session_timeout || 3600;
            if (bcryptRounds) bcryptRounds.value = config.security?.bcrypt_rounds || 12;

        } catch (error) {
            console.error('Erreur lors du chargement de la configuration:', error);
        }
    }

    async loadSessions() {
        try {
            const response = await fetch('/admin/sessions');
            const sessions = await response.json();

            const container = document.getElementById('sessions-list');
            if (container) {
                if (sessions.sessions && sessions.sessions.length > 0) {
                    container.innerHTML = sessions.sessions.map(session => `
                        <div class="flex items-center justify-between p-3 bg-gray-800 rounded-lg">
                            <div class="flex items-center space-x-3">
                                <span class="text-2xl">👤</span>
                                <div>
                                    <p class="font-medium">${session.username}</p>
                                    <p class="text-sm text-gray-400">Connecté le ${session.login_time}</p>
                                </div>
                            </div>
                            <div class="flex items-center space-x-3">
                                <span class="text-sm text-gray-400">Expire dans ${Math.round(session.remaining_time / 60)} min</span>
                                <button class="text-xs bg-red-600 hover:bg-red-700 px-2 py-1 rounded" onclick="adminApp.terminateSession('${session.username}')">
                                    🚫 Terminer
                                </button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = `
                        <div class="text-gray-400 text-center py-8">
                            Aucune session active
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Erreur lors du chargement des sessions:', error);
        }
    }

    async loadLogs() {
        try {
            const response = await fetch('/admin/logs');
            const logs = await response.json();

            const container = document.getElementById('logs-container');
            if (container) {
                if (logs.logs && logs.logs.length > 0) {
                    container.innerHTML = logs.logs.map(log => `
                        <div class="log-entry text-sm mb-2">
                            <span class="text-gray-400">[${log.timestamp}]</span>
                            <span class="text-${this.getLogLevelColor(log.level)}">${log.level}</span>
                            <span class="text-white">${log.message}</span>
                        </div>
                    `).join('');

                    // Auto-scroll vers le bas
                    container.scrollTop = container.scrollHeight;
                } else {
                    container.innerHTML = `
                        <div class="text-gray-400 text-center py-8">
                            Aucun log disponible
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Erreur lors du chargement des logs:', error);
        }
    }

    getLogLevelColor(level) {
        switch (level.toUpperCase()) {
            case 'ERROR': return 'red-400';
            case 'WARNING': return 'yellow-400';
            case 'INFO': return 'blue-400';
            default: return 'gray-400';
        }
    }

    async saveSystemConfig(event) {
        event.preventDefault();

        try {
            const formData = {
                app: {
                    name: document.getElementById('app-name').value,
                    version: document.getElementById('app-version').value,
                    debug: document.getElementById('debug-mode').value === 'true'
                }
            };

            const response = await fetch('/config/app', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.showNotification('Configuration système sauvegardée', 'success');
            } else {
                this.showNotification('Erreur lors de la sauvegarde', 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la sauvegarde:', error);
            this.showNotification('Erreur lors de la sauvegarde', 'error');
        }
    }

    async saveSecurityConfig(event) {
        event.preventDefault();

        try {
            const formData = {
                security: {
                    session_timeout: parseInt(document.getElementById('session-timeout').value),
                    bcrypt_rounds: parseInt(document.getElementById('bcrypt-rounds').value)
                }
            };

            const response = await fetch('/config/security', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                this.showNotification('Configuration de sécurité sauvegardée', 'success');
            } else {
                this.showNotification('Erreur lors de la sauvegarde', 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la sauvegarde:', error);
            this.showNotification('Erreur lors de la sauvegarde', 'error');
        }
    }

    async logout() {
        try {
            const response = await fetch('/admin/logout', {
                method: 'POST'
            });

            if (response.ok) {
                // Rediriger vers la page principale
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Erreur lors de la déconnexion:', error);
            // Rediriger quand même
            window.location.href = '/';
        }
    }

    async restartSystem() {
        if (confirm('Êtes-vous sûr de vouloir redémarrer le système ?')) {
            try {
                const response = await fetch('/admin/system/restart', {
                    method: 'POST'
                });

                if (response.ok) {
                    this.showNotification('Redémarrage en cours...', 'info');
                } else {
                    this.showNotification('Erreur lors du redémarrage', 'error');
                }
            } catch (error) {
                console.error('Erreur lors du redémarrage:', error);
                this.showNotification('Erreur lors du redémarrage', 'error');
            }
        }
    }

    async backupSystem() {
        try {
            const response = await fetch('/admin/system/backup', {
                method: 'POST'
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `photobooth_backup_${Date.now()}.zip`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                this.showNotification('Sauvegarde téléchargée', 'success');
            } else {
                this.showNotification('Erreur lors de la sauvegarde', 'error');
            }
        } catch (error) {
            console.error('Erreur lors de la sauvegarde:', error);
            this.showNotification('Erreur lors de la sauvegarde', 'error');
        }
    }

    async clearCache() {
        if (confirm('Êtes-vous sûr de vouloir vider le cache ?')) {
            try {
                const response = await fetch('/admin/system/cache/clear', {
                    method: 'POST'
                });

                if (response.ok) {
                    this.showNotification('Cache vidé avec succès', 'success');
                } else {
                    this.showNotification('Erreur lors du vidage du cache', 'error');
                }
            } catch (error) {
                console.error('Erreur lors du vidage du cache:', error);
                this.showNotification('Erreur lors du vidage du cache', 'error');
            }
        }
    }

    async exportLogs() {
        try {
            const response = await fetch('/admin/logs/export');

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `photobooth_logs_${Date.now()}.txt`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                this.showNotification('Logs exportés avec succès', 'success');
            } else {
                this.showNotification('Erreur lors de l\'export des logs', 'error');
            }
        } catch (error) {
            console.error('Erreur lors de l\'export des logs:', error);
            this.showNotification('Erreur lors de l\'export des logs', 'error');
        }
    }

    async downloadPhoto(filename) {
        try {
            const response = await fetch(`/uploads/${filename}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                this.showNotification('Photo téléchargée', 'success');
            }
        } catch (error) {
            console.error('Erreur lors du téléchargement:', error);
            this.showNotification('Erreur lors du téléchargement', 'error');
        }
    }

    async deletePhoto(filename) {
        if (confirm(`Êtes-vous sûr de vouloir supprimer la photo "${filename}" ?`)) {
            try {
                const response = await fetch(`/admin/photos/${filename}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.showNotification('Photo supprimée', 'success');
                    this.loadPhotos(); // Recharger la liste
                } else {
                    this.showNotification('Erreur lors de la suppression', 'error');
                }
            } catch (error) {
                console.error('Erreur lors de la suppression:', error);
                this.showNotification('Erreur lors de la suppression', 'error');
            }
        }
    }

    async terminateSession(username) {
        if (confirm(`Êtes-vous sûr de vouloir terminer la session de "${username}" ?`)) {
            try {
                const response = await fetch(`/admin/sessions/${username}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    this.showNotification('Session terminée', 'success');
                    this.loadSessions(); // Recharger la liste
                } else {
                    this.showNotification('Erreur lors de la terminaison', 'error');
                }
            } catch (error) {
                console.error('Erreur lors de la terminaison:', error);
                this.showNotification('Erreur lors de la terminaison', 'error');
            }
        }
    }

    async terminateAllSessions() {
        if (confirm('Êtes-vous sûr de vouloir terminer toutes les sessions actives ?')) {
            try {
                const response = await fetch('/admin/sessions/terminate-all', {
                    method: 'POST'
                });

                if (response.ok) {
                    this.showNotification('Toutes les sessions ont été terminées', 'success');
                    this.loadSessions(); // Recharger la liste
                } else {
                    this.showNotification('Erreur lors de la terminaison', 'error');
                }
            } catch (error) {
                console.error('Erreur lors de la terminaison:', error);
                this.showNotification('Erreur lors de la terminaison', 'error');
            }
        }
    }

    async clearLogs() {
        if (confirm('Êtes-vous sûr de vouloir effacer tous les logs ?')) {
            try {
                const response = await fetch('/admin/logs/clear', {
                    method: 'POST'
                });

                if (response.ok) {
                    this.showNotification('Logs effacés', 'success');
                    this.loadLogs(); // Recharger les logs
                } else {
                    this.showNotification('Erreur lors de l\'effacement', 'error');
                }
            } catch (error) {
                console.error('Erreur lors de l\'effacement:', error);
                this.showNotification('Erreur lors de l\'effacement', 'error');
            }
        }
    }

    async filterLogs(level) {
        try {
            const response = await fetch(`/admin/logs?level=${level}`);
            const logs = await response.json();

            const container = document.getElementById('logs-container');
            if (container) {
                if (logs.logs && logs.logs.length > 0) {
                    container.innerHTML = logs.logs.map(log => `
                        <div class="log-entry text-sm mb-2">
                            <span class="text-gray-400">[${log.timestamp}]</span>
                            <span class="text-${this.getLogLevelColor(log.level)}">${log.level}</span>
                            <span class="text-white">${log.message}</span>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = `
                        <div class="text-gray-400 text-center py-8">
                            Aucun log trouvé pour ce niveau
                        </div>
                    `;
                }
            }
        } catch (error) {
            console.error('Erreur lors du filtrage des logs:', error);
        }
    }

    searchPhotos(query) {
        // Implémentation simple de recherche côté client
        const photoItems = document.querySelectorAll('.photo-item');
        photoItems.forEach(item => {
            const filename = item.querySelector('p').textContent.toLowerCase();
            if (filename.includes(query.toLowerCase())) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    showNotification(message, type = 'info') {
        // Créer une notification temporaire
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 transition-all duration-300 ${type === 'success' ? 'bg-green-600' :
                type === 'error' ? 'bg-red-600' :
                    type === 'warning' ? 'bg-yellow-600' : 'bg-blue-600'
            }`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Supprimer après 3 secondes
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    startAutoRefresh() {
        // Actualiser automatiquement le tableau de bord toutes les 30 secondes
        this.refreshInterval = setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboard();
            }
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }

    displayPhotos(photos) {
        const photosContainer = document.getElementById('photos-container');
        if (!photosContainer) return;

        if (!photos || photos.length === 0) {
            photosContainer.innerHTML = '<p class="text-gray-500 text-center py-8">Aucune photo trouvée</p>';
            return;
        }

        const photosHTML = photos.map(photo => `
            <div class="bg-white rounded-lg shadow-md p-4 admin-card">
                <div class="flex items-center space-x-4">
                    <div class="flex-shrink-0">
                        <img src="/uploads/${encodeURIComponent(photo.filename)}" 
                             alt="${photo.filename}" 
                             class="w-20 h-20 object-cover rounded-lg border-2 border-gray-200">
                    </div>
                    <div class="flex-1">
                        <h4 class="text-lg font-semibold text-gray-900 truncate">${photo.filename}</h4>
                        <p class="text-sm text-gray-600">Taille: ${photo.size}</p>
                        <p class="text-sm text-gray-600">Date: ${photo.date}</p>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="adminApp.viewPhoto('${photo.filename}')" 
                                class="action-btn bg-blue-500 hover:bg-blue-600 text-white">
                            👁️ Voir
                        </button>
                        <button onclick="adminApp.deletePhoto('${photo.filename}')" 
                                class="action-btn bg-red-500 hover:bg-red-600 text-white">
                            🗑️ Supprimer
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        photosContainer.innerHTML = photosHTML;
    }
    
    viewPhoto(filename) {
        // Ouvrir la photo dans un nouvel onglet
        window.open(`/uploads/${encodeURIComponent(filename)}`, '_blank');
    }
}

// Initialisation de l'application quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    window.adminApp = new AdminApp();
});

// Gestion des erreurs globales
window.addEventListener('error', (event) => {
    console.error('Erreur JavaScript:', event.error);
});

// Gestion des promesses rejetées
window.addEventListener('unhandledrejection', (event) => {
    console.error('Promesse rejetée non gérée:', event.reason);
});

// Nettoyage lors de la fermeture de la page
window.addEventListener('beforeunload', () => {
    if (window.adminApp) {
        window.adminApp.stopAutoRefresh();
    }
});
