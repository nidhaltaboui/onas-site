// Injecte la barre de navigation commune dans l'élément #navbar-container
function chargerNavbar(pageActive) {
  const pages = [
    { href: "dashboards.html", label: "Dashboards" },
    { href: "prediction.html", label: "Prédiction" },
    { href: "anomalies.html", label: "Anomalies" },
  ];

  const liens = pages
    .map(
      (p) =>
        `<a href="${p.href}" class="${p.href === pageActive ? "active" : ""}">${p.label}</a>`
    )
    .join("");

  document.getElementById("navbar-container").innerHTML = `
    <div class="navbar">
      <div class="logo">💧 ONAS Supervision</div>
      <nav>${liens}</nav>
      <div class="user-zone">
        <span id="nom-utilisateur">Utilisateur</span>
        <button class="btn-logout" onclick="deconnexion()">Déconnexion</button>
      </div>
    </div>
  `;

  afficherUtilisateur();
}
