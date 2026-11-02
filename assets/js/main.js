// Divot & Co — landing page behaviour

// Set this to a form backend URL (e.g. a Formspree endpoint like
// "https://formspree.io/f/xxxxxxx") to turn on the email waitlist.
// While it is empty, the page shows the "Follow on Instagram" fallback instead.
const WAITLIST_ENDPOINT = "";

document.getElementById("year").textContent = new Date().getFullYear();

const form = document.getElementById("waitlist-form");
const fallback = document.getElementById("waitlist-fallback");
const statusEl = document.getElementById("form-status");

if (WAITLIST_ENDPOINT) {
  form.hidden = false;
  fallback.hidden = true;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = form.email.value.trim();

    if (!form.email.checkValidity()) {
      statusEl.textContent = "Please enter a valid email address.";
      form.email.focus();
      return;
    }

    const button = form.querySelector("button");
    button.disabled = true;
    statusEl.textContent = "Joining…";

    try {
      const response = await fetch(WAITLIST_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ email }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      form.reset();
      statusEl.textContent = "You're on the list. See you on the first tee. ⛳";
    } catch (error) {
      statusEl.textContent = "Something went wrong. Please try again, or follow @divotcogolf on Instagram.";
    } finally {
      button.disabled = false;
    }
  });
}
