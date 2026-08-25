// ==========================================================
// Fonctions communes : appel API + gestion du jeton de connexion
// ==========================================================

const API_BASE = ""; // vide car le frontend est servi par FastAPI lui-même (même origine)

function getToken() {
  return localStorage.getItem("onas_token");
}

function setToken(token) {
  localStorage.setItem("onas_token", token);
}

function clearToken() {
  localStorage.removeItem("onas_token");
  localStorage.removeItem("onas_nom");
}

/** Redirige vers le login si aucun jeton n'est présent. À appeler en haut de chaque page protégée. */
function exigerConnexion() {
  if (!getToken()) {
    window.location.href = "index.html";
  }
}

/** Wrapper fetch qui ajoute automatiquement le jeton d'authentification. */
async function appelApi(chemin, options = {}) {
  const token = getToken();
  const headers = options.headers || {};
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const reponse = await fetch(`${API_BASE}${chemin}`, { ...options, headers });

  if (reponse.status === 401) {
    clearToken();
    window.location.href = "index.html";
    throw new Error("Session expirée, veuillez vous reconnecter.");
  }

  if (!reponse.ok) {
    const erreur = await reponse.json().catch(() => ({}));
    throw new Error(erreur.detail || "Une erreur est survenue.");
  }

  return reponse.json();
}

function deconnexion() {
  clearToken();
  window.location.href = "index.html";
}

/** Affiche le nom de l'utilisateur connecté dans la barre de navigation, si l'élément existe. */
function afficherUtilisateur() {
  const el = document.getElementById("nom-utilisateur");
  if (el) el.textContent = localStorage.getItem("onas_nom") || "Utilisateur";
}
