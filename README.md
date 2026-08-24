# ONAS - Site de Supervision (Dashboards, Prédiction, Anomalies)

Site web avec :
- **Frontend** : HTML / CSS / JavaScript pur (pas de framework, pas de build à faire)
- **Backend** : FastAPI (Python)

## Structure du projet

```
onas_site/
├── backend/
│   ├── app/
│   │   ├── main.py              # Point d'entrée FastAPI (sert aussi le frontend)
│   │   ├── config.py            # Paramètres (clé secrète, utilisateur démo)
│   │   ├── auth.py               # Logique JWT + mot de passe oublié
│   │   ├── schemas.py            # Modèles Pydantic
│   │   └── routers/
│   │       ├── auth_router.py         # /api/auth/...
│   │       ├── prediction_router.py   # /api/predictions
│   │       └── anomaly_router.py      # /api/anomalies
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html              # Page 1 : Connexion (login)
    ├── forgot-password.html    # Mot de passe oublié
    ├── reset-password.html     # Réinitialisation du mot de passe
    ├── dashboards.html         # Page 2 : Dashboards Power BI
    ├── prediction.html         # Page 3 : Résultats de prédiction (graphiques)
    ├── anomalies.html          # Page 4 : Détection d'anomalies (tableau)
    ├── css/style.css
    └── js/
        ├── api.js       # Appels API + gestion du jeton
        └── navbar.js    # Barre de navigation commune
```

## Installation et lancement (depuis Visual Studio Code)

1. **Ouvrir le dossier** `onas_site` dans VS Code.
2. **Ouvrir un terminal** dans VS Code (Terminal → Nouveau Terminal).
3. Créer un environnement virtuel et installer les dépendances :

   ```bash
   cd backend
   python -m venv venv
   # Windows :
   venv\Scripts\activate
   # macOS/Linux :
   source venv/bin/activate

   pip install -r requirements.txt
   ```

4. **Lancer le serveur** :

   ```bash
   uvicorn app.main:app --reload
   ```

5. Ouvrir le navigateur sur : **http://127.0.0.1:8000**
   (Le frontend est automatiquement servi par FastAPI, pas besoin de Live Server.)

## Connexion de démonstration

- Email : `admin@onas.tn`
- Mot de passe : `onas2026`

(Ces identifiants sont définis dans `backend/app/config.py` — à remplacer par une vraie
table d'utilisateurs en base de données PostgreSQL quand vous serez prêt.)

## Mot de passe oublié — envoi d'un vrai email (Gmail)

Le lien de réinitialisation est maintenant envoyé par **vrai email** via SMTP.
Pour l'activer avec un compte Gmail :

1. Activez la validation en 2 étapes sur le compte Gmail qui enverra les emails
   (obligatoire pour l'étape suivante) : https://myaccount.google.com/security
2. Créez un **mot de passe d'application** :
   https://myaccount.google.com/apppasswords
   → Choisissez "Autre" comme application, donnez-lui un nom (ex: "ONAS Site"),
   copiez le mot de passe généré (16 caractères, sans espaces).
3. Ouvrez le fichier `backend/.env` et remplissez :
   ```
   SMTP_USER=votre-adresse@gmail.com
   SMTP_PASSWORD=le-mot-de-passe-application-genere
   ```
4. Redémarrez le serveur (`uvicorn app.main:app --reload`).

**Sans cette configuration**, le site continue de fonctionner : le lien de
réinitialisation s'affiche simplement dans le terminal (mode secours), pour
ne pas bloquer les tests.

⚠️ Ne committez jamais le fichier `.env` rempli (avec le vrai mot de passe
d'application) dans un dépôt Git public.

## Données de prédiction et d'anomalies

Les endpoints `/api/predictions` et `/api/anomalies` renvoient actuellement des
**données d'exemple** générées pour que le site fonctionne immédiatement.

Pour brancher vos vraies données (issues de votre notebook et de votre base
PostgreSQL / tables `mlops_previsions_versions`, `log_executions_pipeline`, etc.) :

- Modifiez `charger_previsions_depuis_bd()` dans `backend/app/routers/prediction_router.py`
- Modifiez `charger_anomalies_depuis_bd()` dans `backend/app/routers/anomaly_router.py`

et remplacez la génération aléatoire par une vraie requête SQL (via `sqlalchemy`,
déjà utilisé dans votre notebook).

## Page Dashboards Power BI

La page `dashboards.html` intègre directement l'iframe Power BI que vous avez
fournie. Pour que l'authentification `autoAuth=true` fonctionne, l'utilisateur
doit être connecté à son compte Power BI (avec les droits d'accès au rapport)
dans le même navigateur.

## Sécurité — points à adresser avant une mise en production réelle

- Remplacer `SECRET_KEY` dans `.env` par une valeur longue et aléatoire (ne jamais la committer).
- Remplacer le stockage des utilisateurs en mémoire par une vraie base de données.
- Brancher un vrai service d'envoi d'email pour le mot de passe oublié.
- Restreindre `allow_origins` dans `main.py` (CORS) à votre domaine réel.
- Utiliser HTTPS en production.
