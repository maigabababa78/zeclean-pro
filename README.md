# ZeClean Pro — Application de Gestion d'une Société de Nettoyage

Application web complète et responsive développée avec **Python (Django 5)**, **TailwindCSS**, **HTMX** et **Alpine.js**, configurée pour le contexte **Franc CFA (FCFA / TVA 18%)** et prête pour **PostgreSQL**.

## 🚀 Démarrage Rapide

Double-cliquez sur **`lancer_application.bat`** ou exécutez dans le terminal :

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Puis ouvrez votre navigateur sur : **http://127.0.0.1:8000**

## 👥 Comptes de Démonstration (Connexion en 1 clic disponible sur la page d'accueil)

| Profil | Identifiant | Mot de passe | Rôle & Accès |
|--------|-------------|--------------|--------------|
| **Administrateur / Gérant** | `admin` | `admin123` | Accès total (KPIs, Clients, Contrats, Devis, Facturation FCFA, RH, Stocks) |
| **Chef d'équipe / Superviseur** | `superviseur` | `superviseur123` | Planning, Équipes, Pointage terrain, Contrôles qualité, Stocks |
| **Agent d'entretien** | `agent` | `agent123` | Consultation de son planning, pointage arrivée/départ, validation des checklists |
| **Client (Portail)** | `client` | `client123` | Suivi des interventions sur ses sites, rapports qualité et factures |

## 🐘 Activer PostgreSQL

Le connecteur `psycopg[binary]` est déjà installé. Dès que votre serveur PostgreSQL est actif :
1. Ouvrez le fichier `.env`
2. Passez `USE_POSTGRESQL=True` et renseignez vos identifiants (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
3. Lancez :
   ```powershell
   .\.venv\Scripts\python.exe manage.py migrate
   .\.venv\Scripts\python.exe manage.py seed_demo
   ```
