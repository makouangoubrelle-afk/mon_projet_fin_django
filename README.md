# SGHL — Système de Gestion Hospitalière et de Laboratoire

ERP médical intégré : patients, médecins, infirmiers, secrétaires, géolocalisation, banque de sang.

## Prérequis

- Python 3.11+
- **PostgreSQL 14+** (base de données obligatoire)
- Node.js 18+
- npm

## 1. Backend (Django)

### PostgreSQL

Créez la base de données :

```sql
CREATE DATABASE sghl;
CREATE USER sghl_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE sghl TO sghl_user;
```

Copiez la configuration :

```powershell
copy .env.example .env
# Éditez .env : POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
```

```powershell
cd C:\Users\makou\mon_projet_fin_django

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Installer les dépendances (psycopg pour PostgreSQL)
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer les données de démonstration (comptes, services, banque de sang)
python manage.py seed_hospital

# Lancer le serveur API
python manage.py runserver
```

> **Mode local sans PostgreSQL** : ajoutez `USE_SQLITE=true` dans `.env` (développement uniquement).

L'API est disponible sur : **http://127.0.0.1:8000/api/docs**

## 2. Frontend (Vue 3 + Tailwind)

Ouvrir un **second terminal** :

```powershell
cd C:\Users\makou\mon_projet_fin_django\sih-frontend

npm install
npm run dev
```

L'application est disponible sur : **http://localhost:5173**

## Connexion par email (code à usage unique)

1. Entrez votre **adresse email** sur la page de connexion
2. Un **code à 6 chiffres** est généré et envoyé **automatiquement** par email
3. Le code est **renouvelé à chaque connexion** et expire après 10 minutes
4. Entrez le code reçu pour accéder à l'application

### Emails de démonstration

| Email | Rôle |
|-------|------|
| `admin@sghl.com` | Administrateur |
| `medecin@sghl.com` | Médecin |
| `infirmier@sghl.com` | Infirmier |
| `secretaire@sghl.com` | Secrétaire |
| `patient@sghl.com` | Patient |

### Configurer l'envoi email (Gmail)

Copiez `.env.example` en `.env` et remplissez vos identifiants Gmail :

```powershell
copy .env.example .env
# Éditez .env avec votre email et mot de passe d'application Gmail
```

Sans configuration email, le code s'affiche à l'écran (mode développement) et dans le terminal Django.

## Comptes de démonstration (legacy)

| Identifiant | Mot de passe | Rôle |
|-------------|--------------|------|
| `admin` | `admin123` | Administrateur |
| `medecin` | `medecin123` | Médecin |
| `infirmier` | `infirmier123` | Infirmier |
| `secretaire` | `sec123` | Secrétaire (Cardiologie) |
| `reception` | `recep123` | Réceptionniste |
| `patient` | `patient123` | Patient |

## Fonctionnalités

- **Connexion multi-rôles** : menu adapté selon le profil (patient, médecin, infirmier, secrétaire…)
- **Services & secrétariat** : chaque service a une secrétaire attitrée
- **Géolocalisation** : suivi de la position du patient (bâtiment, étage, salle, GPS)
- **Banque de sang** : stock par groupe sanguin avec alertes stock critique
- **Patients, consultations, chambres, labo, pharmacie, facturation**

## En cas de problème de base de données

```powershell
python fix_db.py
python manage.py migrate
python manage.py seed_hospital
```
