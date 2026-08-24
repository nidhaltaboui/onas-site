import os
from pathlib import Path

# ==== Chargement du fichier .env (s'il existe) ====
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass  # python-dotenv n'est pas installé : les variables d'environnement système seront utilisées telles quelles

# ==== Paramètres de sécurité ====
# ⚠️ En production, mettez ces valeurs dans un fichier .env (voir .env.example)
SECRET_KEY = os.getenv("SECRET_KEY", "changez-cette-cle-secrete-en-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 heures

# ==== Paramètres d'envoi d'email (SMTP) — pour le "mot de passe oublié" ====
# Voir le README pour la marche à suivre avec un compte Gmail (mot de passe
# d'application requis, pas votre mot de passe Gmail normal).
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "ONAS Supervision")
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")

# ==== Utilisateur(s) de démonstration ====
# Remplacez par une vraie table "utilisateurs" en base de données quand vous serez prêt.
# Mot de passe par défaut : "onas2026" (hashé au premier import, voir auth.py)
DEMO_USERS = {
    "admin@onas.tn": {
        "nom": "Administrateur ONAS",
        "password_plain": "onas2026",  # utilisé uniquement pour générer le hash au démarrage
    },
    "nidhaltaboui5@gmail.com": {
        "nom": "Nidhal Taboui",
        "password_plain": "onas2026",
    },
}
