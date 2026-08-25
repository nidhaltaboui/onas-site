from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import auth_router, prediction_router, anomaly_router

app = FastAPI(
    title="ONAS - Plateforme de Supervision",
    description="API pour les tableaux de bord Power BI, les prédictions et la détection d'anomalies.",
    version="1.0.0",
)

# CORS : utile si un jour le frontend est servi séparément (ex: Live Server VS Code)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(prediction_router.router)
app.include_router(anomaly_router.router)

# ==== Sert le frontend (HTML/CSS/JS) directement depuis FastAPI ====
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
