"""
Endpoints de détection d'anomalies.

⚠️ Comme pour les prédictions : remplacez `charger_anomalies_depuis_bd`
par une vraie requête vers votre base (probablement une table
`anomalies_detectees` alimentée par votre pipeline z-score intra-mois,
d'après votre notebook).
"""

import random
from datetime import date, timedelta

from fastapi import APIRouter, Depends

from .auth_router import utilisateur_courant

router = APIRouter(prefix="/api/anomalies", tags=["Anomalies"])

EQUIPEMENTS = ["Pompe P1", "Pompe P2", "Aérateur A1", "Dégrilleur D1", "Décanteur D2"]
SERIES = ["debit_m3", "charge_kg", "energie_kwh", "boues_m3"]

# Les anomalies sont détectées sur les données réelles de l'année 2025
DATE_DEBUT_2025 = date(2025, 1, 1)
DATE_FIN_2025 = date(2025, 12, 31)
PLAGE_JOURS_2025 = (DATE_FIN_2025 - DATE_DEBUT_2025).days


def charger_anomalies_depuis_bd(limite: int = 30):
    """
    TODO: remplacer par une vraie requête SQL sur la table des anomalies
    détectées par le pipeline (z-score intra-mois > seuil, cf. notebook).
    Pour l'instant : génère des exemples réalistes.
    """
    random.seed(7)
    anomalies = []
    for i in range(limite):
        jour = DATE_DEBUT_2025 + timedelta(days=random.randint(0, PLAGE_JOURS_2025))
        serie = random.choice(SERIES)
        z_score = round(random.uniform(2.0, 4.5) * random.choice([-1, 1]), 2)
        type_anomalie = "rupture" if abs(z_score) > 3.2 else "transition"
        anomalies.append(
            {
                "date": jour.isoformat(),
                "equipement": random.choice(EQUIPEMENTS),
                "serie": serie,
                "z_score": z_score,
                "type_anomalie": type_anomalie,
                "ecart_pct": round(z_score * 12.5, 1),
                "severite": "haute" if abs(z_score) > 3.2 else "moyenne",
            }
        )
    anomalies.sort(key=lambda a: a["date"], reverse=True)
    return anomalies


@router.get("")
def obtenir_anomalies(limite: int = 30, email: str = Depends(utilisateur_courant)):
    """Renvoie la liste des anomalies détectées récemment (triées, plus récentes d'abord)."""
    anomalies = charger_anomalies_depuis_bd(limite)
    resume = {
        "total": len(anomalies),
        "haute_severite": len([a for a in anomalies if a["severite"] == "haute"]),
        "moyenne_severite": len([a for a in anomalies if a["severite"] == "moyenne"]),
    }
    return {"resume": resume, "anomalies": anomalies}