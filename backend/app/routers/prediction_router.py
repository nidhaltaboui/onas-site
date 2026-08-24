"""
Endpoints de prédiction.

⚠️ Les données ci-dessous sont des exemples générés pour faire fonctionner
le site tout de suite. Remplacez la fonction `charger_previsions_depuis_bd`
par une vraie requête vers votre base PostgreSQL (table mlops_previsions_versions
d'après votre architecture actuelle) pour brancher les vraies prévisions
issues de votre notebook.
"""

import random
from datetime import date

from fastapi import APIRouter, Depends

from .auth_router import utilisateur_courant

router = APIRouter(prefix="/api/predictions", tags=["Prédictions"])

MOIS_FR = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
]

SERIES = {
    "debit_m3": {"label": "Débit (m³/jour)", "base": 3200, "unite": "m³/j"},
    "charge_kg": {"label": "Charge organique (kg/j)", "base": 850, "unite": "kg/j"},
    "energie_kwh": {"label": "Énergie consommée (kWh)", "base": 42000, "unite": "kWh"},
    "boues_m3": {"label": "Boues produites (m³)", "base": 610, "unite": "m³"},
}


def charger_previsions_depuis_bd():
    """
    TODO: remplacer par une vraie requête SQL, ex:
        SELECT mois, serie, valeur_predite, borne_min, borne_max, modele
        FROM mlops_previsions_versions
        WHERE annee = 2026 AND version = (SELECT MAX(version) ...)
    Pour l'instant : génère des données d'exemple cohérentes avec vos séries.
    """
    random.seed(42)
    resultat = {}
    for code, infos in SERIES.items():
        valeurs = []
        base = infos["base"]
        for i, mois in enumerate(MOIS_FR):
            tendance = base * (1 + 0.01 * i)
            saisonnalite = 1 + 0.08 * random.uniform(-1, 1)
            valeur = round(tendance * saisonnalite, 1)
            marge = valeur * 0.07
            valeurs.append(
                {
                    "mois": mois,
                    "valeur_predite": valeur,
                    "borne_min": round(valeur - marge, 1),
                    "borne_max": round(valeur + marge, 1),
                }
            )
        resultat[code] = {
            "label": infos["label"],
            "unite": infos["unite"],
            "valeurs": valeurs,
        }
    return resultat


@router.get("")
def obtenir_previsions(email: str = Depends(utilisateur_courant)):
    """Renvoie les prévisions 2026 pour toutes les séries (débit, charge, énergie, boues)."""
    return {
        "annee": 2026,
        "genere_le": date.today().isoformat(),
        "series": charger_previsions_depuis_bd(),
    }


@router.get("/{code_serie}")
def obtenir_prevision_serie(code_serie: str, email: str = Depends(utilisateur_courant)):
    """Renvoie la prévision d'une seule série (debit_m3, charge_kg, energie_kwh, boues_m3)."""
    donnees = charger_previsions_depuis_bd()
    if code_serie not in donnees:
        return {"erreur": f"Série inconnue: {code_serie}", "series_disponibles": list(donnees.keys())}
    return donnees[code_serie]
