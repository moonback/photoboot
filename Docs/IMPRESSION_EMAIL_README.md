# Fonctionnalités d'Impression et d'Email - Photobooth

## Vue d'ensemble

Ce document décrit les nouvelles fonctionnalités d'impression et d'envoi d'email ajoutées au Photobooth. Ces fonctionnalités sont conçues pour être **Windows-first** avec un support optionnel pour d'autres plateformes.

## 🖨️ Impression

### Fonctionnalités

- **Support Windows natif** via `win32print` (pywin32)
- **Fallback Unix/Linux** via `lpr` (si disponible)
- **Gestion des imprimantes** : énumération, sélection, statut
- **Formats de papier** : 4x6, 5x7, 6x8, A4, Letter
- **Gestion des erreurs** avec retry automatique
- **Rate limiting** : 5 impressions par minute par IP
- **Préparation d'image** automatique (redimensionnement, conversion)

### Configuration

```yaml
printing:
  default_printer: ""                    # Imprimante par défaut (vide = système)
  paper_size: "4x6"                     # Format papier par défaut
  quality: "normal"                      # Qualité d'impression
  max_copies: 5                          # Nombre max de copies
  retry_attempts: 3                      # Tentatives en cas d'échec
  retry_delay: 2                         # Délai entre tentatives (secondes)
```

### Variables d'environnement

```bash
PRINTING_DEFAULT_PRINTER=HP_Printer
PRINTING_PAPER_SIZE=4x6
PRINTING_QUALITY=normal
PRINTING_MAX_COPIES=5
PRINTING_RETRY_ATTEMPTS=3
PRINTING_RETRY_DELAY=2
```

### API Endpoints

- `GET /print/printers` - Liste des imprimantes disponibles
- `GET /print/status/{printer_name}` - Statut d'une imprimante
- `POST /print/photo` - Impression d'une photo
- `GET /print/test` - Test de connectivité

### Utilisation

```javascript
// Impression d'une photo
const response = await fetch('/print/photo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        photo_path: '/path/to/photo.jpg',
        copies: 2,
        printer_name: 'HP_Printer'  // optionnel
    })
});
```

## 📧 Email

### Fonctionnalités

- **Support SMTP complet** avec TLS/SSL
- **Pièces jointes** : miniature + photo originale
- **Consentement RGPD** configurable
- **Rate limiting** : 10 emails par heure par IP
- **Validation email** côté client et serveur
- **Gestion des erreurs** détaillée
- **Templates personnalisables** pour sujet et contenu

### Configuration

```yaml
email:
  smtp_server: "smtp.gmail.com"         # Serveur SMTP
  smtp_port: 587                         # Port SMTP
  smtp_use_tls: true                     # Utiliser TLS
  smtp_use_ssl: false                    # Utiliser SSL
  smtp_username: "your-email@gmail.com"  # Identifiant SMTP
  smtp_password: "your-app-password"     # Mot de passe SMTP
  from_email: "your-email@gmail.com"     # Email expéditeur
  from_name: "Photobooth"                # Nom expéditeur
  gdpr_consent_required: true            # Consentement RGPD requis
  gdpr_retention_days: 30                # Rétention des données
  rate_limit_emails: 10                  # Limite d'emails par heure
```

### Variables d'environnement

```bash
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USE_TLS=true
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_FROM_EMAIL=your-email@gmail.com
EMAIL_GDPR_CONSENT_REQUIRED=true
EMAIL_GDPR_RETENTION_DAYS=30
```

### API Endpoints

- `GET /email/gdpr-consent` - Texte de consentement RGPD
- `POST /email/send` - Envoi d'un email
- `GET /email/status` - Statut du service email
- `GET /email/test` - Test de connectivité
- `POST /email/validate-email` - Validation format email

### Utilisation

```javascript
// Envoi d'un email
const response = await fetch('/email/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        to_email: 'user@example.com',
        photo_path: '/path/to/photo.jpg',
        download_link: 'https://example.com/download/photo',
        consent_given: true,
        user_name: 'John Doe'
    })
});
```

## 🔒 Sécurité

### Rate Limiting

- **Impression** : 5 demandes par minute par IP
- **Email** : 10 envois par heure par IP
- **Sessions** : Cookies HttpOnly avec signature
- **Validation** : Vérification des paramètres côté serveur

### RGPD

- **Consentement explicite** requis pour l'email
- **Rétention configurable** des données
- **Texte personnalisable** de consentement
- **Audit trail** des consentements

## 🚀 Installation

### Dépendances

```bash
pip install -r requirements.txt
```

### Dépendances Windows

```bash
pip install pywin32>=306
```

### Dépendances optionnelles

```bash
pip install psutil>=5.9.0  # Pour le monitoring système
```

## 📋 Configuration

### 1. Copier le template d'environnement

```bash
cp env_template.txt config/.env
```

### 2. Modifier la configuration

Éditer `config/.env` avec vos paramètres :

```bash
# Impression
PRINTING_DEFAULT_PRINTER=HP_Photosmart_Printer

# Email
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_USERNAME=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
```

### 3. Vérifier la configuration

```bash
# Test impression
curl http://localhost:8000/print/test

# Test email
curl http://localhost:8000/email/test
```

## 🧪 Tests

### Test d'impression

```bash
# Lister les imprimantes
curl http://localhost:8000/print/printers

# Tester l'impression
curl -X POST http://localhost:8000/print/photo \
  -H "Content-Type: application/json" \
  -d '{"photo_path": "/path/to/test.jpg", "copies": 1}'
```

### Test d'email

```bash
# Vérifier le statut
curl http://localhost:8000/email/status

# Tester l'envoi
curl -X POST http://localhost:8000/email/send \
  -H "Content-Type: application/json" \
  -d '{"to_email": "test@example.com", "photo_path": "/path/to/test.jpg", "download_link": "https://example.com/download", "consent_given": true}'
```

## 🔧 Dépannage

### Problèmes d'impression

1. **Vérifier les dépendances Windows**
   ```bash
   pip install pywin32>=306
   ```

2. **Vérifier les permissions d'imprimante**
   - L'utilisateur doit avoir accès aux imprimantes
   - Vérifier le spooler d'impression Windows

3. **Tester la connectivité**
   ```bash
   curl http://localhost:8000/print/test
   ```

### Problèmes d'email

1. **Vérifier la configuration SMTP**
   - Serveur, port, TLS/SSL
   - Identifiants et mot de passe

2. **Vérifier les paramètres Gmail**
   - Activer l'authentification à 2 facteurs
   - Générer un mot de passe d'application

3. **Tester la connectivité**
   ```bash
   curl http://localhost:8000/email/test
   ```

## 📊 Monitoring

### Healthcheck enrichi

```bash
curl http://localhost:8000/health
```

Retourne :
- Statut de la caméra
- Espace disque disponible
- Statut des imprimantes
- Statut du service email

### Healthcheck détaillé

```bash
curl http://localhost:8000/health/detailed
```

Retourne des informations complètes sur tous les composants.

## 🎯 Fonctionnalités futures

- **Impression en lot** de plusieurs photos
- **Sauvegarde cloud** des photos
- **Notifications push** pour l'impression
- **Historique** des impressions et envois
- **Statistiques** d'utilisation
- **API webhook** pour intégrations tierces

## 📞 Support

Pour toute question ou problème :

1. Vérifier les logs dans `logs/`
2. Consulter le healthcheck `/health`
3. Tester les endpoints de test
4. Vérifier la configuration dans `config/`

---

**Note** : Ces fonctionnalités sont conçues pour être robustes et sécurisées en production. Assurez-vous de configurer correctement les paramètres de sécurité et de surveiller l'utilisation.
