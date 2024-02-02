const textarea = document.querySelector("textarea");

textarea.addEventListener("input", e => {
    textarea.style.height = "59px"; // Ajustez la hauteur à une valeur légèrement inférieure à la hauteur initiale
    let scHeight = e.target.scrollHeight;
    textarea.style.height = `${Math.min(100, Math.max(60, scHeight))}px`; // Limitez la hauteur à 100px, mais assurez-vous qu'elle reste au moins à 60px
});

// Ajoutez un écouteur d'événements pour réinitialiser la hauteur lorsque le focus est perdu
textarea.addEventListener("blur", () => {
    textarea.style.height = "60px";
});
