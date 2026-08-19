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
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = form.querySelector('button[type="submit"]');
    const payload = Object.fromEntries(new FormData(form).entries());
    const endpoint = form.action.replace("formsubmit.co/", "formsubmit.co/ajax/");

    payload._replyto = payload.email;
    submitButton.disabled = true;
    form.setAttribute("aria-busy", "true");

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      const result = await response.json();

      if (!response.ok || result.success === false || result.success === "false") {
        throw new Error("Form submission failed");
      }

      form.reset();
      if (previewDialog.open) closeDialog();
      showToast("Thank you—your email has been sent to KoriKatha.");
    } catch (error) {
      showToast("We couldn't send that right now. Please email houseofkorikatha@gmail.com directly.");
    } finally {
      submitButton.disabled = false;
      form.removeAttribute("aria-busy");
    }
  });
});

if (new URLSearchParams(window.location.search).get("subscribed") === "true") {
  showToast("Thank you—your email has been sent to KoriKatha.");
  window.history.replaceState({}, "", `${window.location.pathname}#newsletter-title`);
}

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
