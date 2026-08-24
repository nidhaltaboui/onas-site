from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from .. import auth
from ..schemas import (
    LoginRequest,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/api/auth", tags=["Authentification"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def utilisateur_courant(token: str | None = Depends(oauth2_scheme)):
    """Dépendance à utiliser sur les routes protégées."""
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    payload = auth.decoder_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Jeton invalide ou expiré")
    return payload["sub"]


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = auth.authentifier_utilisateur(data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    token = auth.creer_token_acces({"sub": data.email})
    return TokenResponse(access_token=token, nom=user["nom"])


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    jeton = auth.generer_jeton_reinitialisation(data.email)
    if jeton:
        auth.envoyer_email_reinitialisation(data.email, jeton)
    # Pour ne pas révéler si un email existe ou non, on répond toujours pareil.
    return {
        "message": "Si cet email existe dans notre système, un lien de "
        "réinitialisation vient d'être envoyé."
    }


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    ok = auth.reinitialiser_mot_de_passe(data.token, data.nouveau_mot_de_passe)
    if not ok:
        raise HTTPException(status_code=400, detail="Jeton invalide ou expiré")
    return {"message": "Mot de passe réinitialisé avec succès."}


@router.get("/me")
def me(email: str = Depends(utilisateur_courant)):
    user = auth.utilisateurs_db.get(email)
    return {"email": email, "nom": user["nom"] if user else email}
