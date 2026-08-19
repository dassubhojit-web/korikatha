const header = document.querySelector("[data-header]");
const menuButton = document.querySelector("[data-menu-button]");
const mobileMenu = document.querySelector("[data-mobile-menu]");
const previewDialog = document.querySelector("[data-preview-dialog]");
const dialogTitle = document.querySelector("[data-dialog-title]");
const toast = document.querySelector("[data-toast]");

const setHeaderState = () => {
  header.classList.toggle("is-fixed", window.scrollY > 80);
};

setHeaderState();
window.addEventListener("scroll", setHeaderState, { passive: true });

const closeMenu = () => {
  menuButton.setAttribute("aria-expanded", "false");
  mobileMenu.classList.remove("is-open");
  document.body.classList.remove("menu-open");
};

menuButton.addEventListener("click", () => {
  const isOpen = menuButton.getAttribute("aria-expanded") === "true";
  menuButton.setAttribute("aria-expanded", String(!isOpen));
  mobileMenu.classList.toggle("is-open", !isOpen);
  document.body.classList.toggle("menu-open", !isOpen);
});

mobileMenu.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));

const showToast = (message = "Welcome to the KoriKatha family.") => {
  toast.querySelector("p").textContent = message;
  toast.classList.add("is-visible");
  window.setTimeout(() => toast.classList.remove("is-visible"), 3600);
};

document.querySelectorAll("[data-shop]").forEach((button) => {
  button.addEventListener("click", () => {
    closeMenu();
    dialogTitle.textContent = button.dataset.shop;
    previewDialog.showModal();
    document.body.classList.add("dialog-open");
  });
});

const closeDialog = () => {
  previewDialog.close();
  document.body.classList.remove("dialog-open");
};

document.querySelector("[data-dialog-close]").addEventListener("click", closeDialog);
previewDialog.addEventListener("click", (event) => {
  if (event.target === previewDialog) closeDialog();
});
previewDialog.addEventListener("close", () => document.body.classList.remove("dialog-open"));

document.querySelectorAll("[data-newsletter-form], [data-dialog-form]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    form.reset();
    if (previewDialog.open) closeDialog();
    showToast();
  });
});

const revealObserver = new IntersectionObserver(
  (entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.14 }
);

document.querySelectorAll(".reveal").forEach((element) => revealObserver.observe(element));
document.querySelector("[data-year]").textContent = new Date().getFullYear();
