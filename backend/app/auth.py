"""
Gestion de l'authentification : login (JWT) + mot de passe oublié.

⚠️ Implémentation de démonstration :
- Les utilisateurs sont stockés en mémoire (dict). Remplacez par une vraie
  table PostgreSQL quand vous serez prêt (vous avez déjà une base Postgres
  pour le projet, d'après vos échanges précédents).
- Le "mot de passe oublié" génère un jeton temporaire et l'affiche dans les
  logs du serveur (au lieu d'envoyer un vrai email). Pour un envoi réel,
  branchez un service SMTP (ex: smtplib, ou un service comme SendGrid) dans
  la fonction `envoyer_email_reinitialisation`.

Note technique : le hashage des mots de passe utilise directement la
librairie `bcrypt` (et non `passlib`), pour éviter les problèmes de
compatibilité entre passlib et les versions récentes de bcrypt (>=4.1).
"""

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from .config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    DEMO_USERS,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    SMTP_FROM_NAME,
    SITE_URL,
)

# bcrypt a une limite de 72 octets par mot de passe : on tronque par sécurité.
_LIMITE_OCTETS_BCRYPT = 72


def _hasher_mot_de_passe(mot_de_passe_clair: str) -> str:
    mdp_bytes = mot_de_passe_clair.encode("utf-8")[:_LIMITE_OCTETS_BCRYPT]
    return bcrypt.hashpw(mdp_bytes, bcrypt.gensalt()).decode("utf-8")


def verifier_mot_de_passe(mot_de_passe_clair: str, mot_de_passe_hash: str) -> bool:
    mdp_bytes = mot_de_passe_clair.encode("utf-8")[:_LIMITE_OCTETS_BCRYPT]
    return bcrypt.checkpw(mdp_bytes, mot_de_passe_hash.encode("utf-8"))


# ---- Construction de la base "utilisateurs" en mémoire au démarrage ----
utilisateurs_db = {}
for email, infos in DEMO_USERS.items():
    utilisateurs_db[email] = {
        "nom": infos["nom"],
        "password_hash": _hasher_mot_de_passe(infos["password_plain"]),
    }

# ---- Stockage temporaire des jetons de réinitialisation (email -> jeton) ----
reset_tokens: dict[str, dict] = {}


def authentifier_utilisateur(email: str, mot_de_passe: str):
    user = utilisateurs_db.get(email)
    if not user:
        return None
    if not verifier_mot_de_passe(mot_de_passe, user["password_hash"]):
        return None
    return user


def creer_token_acces(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decoder_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generer_jeton_reinitialisation(email: str) -> str | None:
    """Génère un jeton temporaire (valide 30 min) pour réinitialiser le mot de passe."""
    if email not in utilisateurs_db:
        return None
    jeton = secrets.token_urlsafe(32)
    reset_tokens[jeton] = {
        "email": email,
        "expire": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    return jeton


def envoyer_email_reinitialisation(email: str, jeton: str):
    """
    Envoie un vrai email de réinitialisation via SMTP (ex: Gmail).
    Si SMTP_USER / SMTP_PASSWORD ne sont pas configurés dans le fichier .env,
    l'email n'est pas envoyé mais le lien est affiché dans la console du
    serveur en secours, pour ne pas bloquer les tests.
    """
    lien = f"{SITE_URL}/reset-password.html?token={jeton}"

    if not SMTP_USER or not SMTP_PASSWORD:
        print("=" * 70)
        print("[ATTENTION] SMTP_USER / SMTP_PASSWORD non configurés dans .env")
        print(f"[SIMULATION EMAIL] Réinitialisation de mot de passe pour {email}")
        print(f"Lien (valide 30 min) : {lien}")
        print("=" * 70)
        return

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    message = MIMEMultipart("alternative")
    message["Subject"] = "Réinitialisation de votre mot de passe - ONAS Supervision"
    message["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
    message["To"] = email

    texte = (
        "Bonjour,\n\n"
        "Vous avez demandé la réinitialisation de votre mot de passe sur la "
        "plateforme de supervision ONAS.\n\n"
        f"Cliquez sur ce lien pour choisir un nouveau mot de passe (valide 30 minutes) :\n{lien}\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, ignorez simplement cet email.\n\n"
        "— ONAS Supervision"
    )
    html = f"""
    <div style="font-family: Arial, sans-serif; color:#333; max-width:480px; margin:auto;">
      <h2 style="color:#005BAC;">Réinitialisation de mot de passe</h2>
      <p>Bonjour,</p>
      <p>Vous avez demandé la réinitialisation de votre mot de passe sur la
      plateforme de supervision <strong>ONAS</strong>.</p>
      <p style="text-align:center; margin:2rem 0;">
        <a href="{lien}" style="background:#005BAC; color:white; padding:12px 24px;
        border-radius:8px; text-decoration:none; font-weight:bold;">
          Choisir un nouveau mot de passe
        </a>
      </p>
      <p style="font-size:0.85rem; color:#888;">Ce lien est valide 30 minutes.
      Si vous n'êtes pas à l'origine de cette demande, ignorez simplement cet email.</p>
    </div>
    """

    message.attach(MIMEText(texte, "plain"))
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as serveur:
            serveur.starttls()
            serveur.login(SMTP_USER, SMTP_PASSWORD)
            serveur.sendmail(SMTP_USER, email, message.as_string())
        print(f"[EMAIL ENVOYÉ] Réinitialisation envoyée à {email}")
    except Exception as e:
        # On n'expose jamais le détail de l'erreur SMTP au client (sécurité),
        # mais on l'affiche dans les logs du serveur pour le débogage.
        print(f"[ERREUR SMTP] Échec d'envoi à {email} : {e}")
        print(f"Lien de secours (à copier manuellement) : {lien}")


def verifier_jeton_reinitialisation(jeton: str):
    entree = reset_tokens.get(jeton)
    if not entree:
        return None
    if datetime.now(timezone.utc) > entree["expire"]:
        del reset_tokens[jeton]
        return None
    return entree["email"]


def reinitialiser_mot_de_passe(jeton: str, nouveau_mot_de_passe: str) -> bool:
    email = verifier_jeton_reinitialisation(jeton)
    if not email:
        return False
    utilisateurs_db[email]["password_hash"] = _hasher_mot_de_passe(nouveau_mot_de_passe)
    del reset_tokens[jeton]
    return True
