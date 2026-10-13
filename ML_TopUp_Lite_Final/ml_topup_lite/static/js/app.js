/* ==========================================================================
   ML TopUp Lite - Vanilla JavaScript
   Handles mobile menu, product selection UI, alert dismissal, and
   client-side validation hints. Server-side validation is ALWAYS also
   enforced in Flask routes - this JS is for UX only.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
  initMobileMenu();
  initProductSelection();
  initAlertAutoDismiss();
  initDeleteConfirmation();
  initGameAccountValidation();
});

/* ---------------------------------------------------------------------- */
/* Mobile navigation menu toggle                                          */
/* ---------------------------------------------------------------------- */
function initMobileMenu() {
  var toggle = document.getElementById("mobileMenuToggle");
  var links = document.getElementById("navLinks");
  if (!toggle || !links) return;

  toggle.addEventListener("click", function () {
    links.classList.toggle("open");
  });
}

/* ---------------------------------------------------------------------- */
/* Product card selection on the top-up page                              */
/* ---------------------------------------------------------------------- */
function initProductSelection() {
  var grid = document.getElementById("productGrid");
  if (!grid) return;

  var cards = grid.querySelectorAll(".selectable-card");
  cards.forEach(function (card) {
    var radio = card.querySelector(".product-radio");
    if (!radio) return;

    radio.addEventListener("change", function () {
      cards.forEach(function (c) { c.classList.remove("is-selected"); });
      if (radio.checked) {
        card.classList.add("is-selected");
      }
    });
  });
}

/* ---------------------------------------------------------------------- */
/* Auto-dismiss flash alerts after a few seconds                          */
/* ---------------------------------------------------------------------- */
function initAlertAutoDismiss() {
  var alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      if (alert && alert.parentElement) {
        alert.style.transition = "opacity 0.3s ease";
        alert.style.opacity = "0";
        setTimeout(function () { alert.remove(); }, 300);
      }
    }, 6000);
  });
}

/* ---------------------------------------------------------------------- */
/* Confirm before destructive delete actions                              */
/* ---------------------------------------------------------------------- */
function initDeleteConfirmation() {
  var forms = document.querySelectorAll(".confirm-delete");
  forms.forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var confirmed = window.confirm("Are you sure you want to delete this? This cannot be undone.");
      if (!confirmed) {
        event.preventDefault();
      }
    });
  });
}

/* ---------------------------------------------------------------------- */
/* Client-side hint validation for Game ID / Server ID (numeric only)     */
/* Note: Flask also validates this server-side - this is UX only.         */
/* ---------------------------------------------------------------------- */
function initGameAccountValidation() {
  var gameIdInput = document.getElementById("game_id");
  var serverIdInput = document.getElementById("server_id");

  [gameIdInput, serverIdInput].forEach(function (input) {
    if (!input) return;
    input.addEventListener("input", function () {
      var digitsOnly = input.value.replace(/[^0-9]/g, "");
      if (input.value !== digitsOnly) {
        input.value = digitsOnly;
      }
    });
  });
}
