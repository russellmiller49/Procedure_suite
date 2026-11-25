// SMART on FHIR OAuth redirect handler: validates state, exchanges the code
// (PKCE) directly with the EHR token endpoint from the browser, stores the
// session in sessionStorage, and returns to the dashboard.

import { completeAuthorization } from "./smartClient.js";

const statusEl = document.getElementById("smartCallbackStatus");
const retryEl = document.getElementById("smartCallbackRetry");

(async () => {
  try {
    const session = await completeAuthorization(new URLSearchParams(window.location.search));
    if (statusEl) {
      statusEl.textContent = `Connected to ${session.issuerName}. Opening the dashboard…`;
    }
    // /ui/smart/callback.html -> /ui/dashboard.html; ?smart=1 scrolls the EHR panel into view.
    // (/ui/ may be the focused demo page, so the dashboard is addressed by name.)
    window.location.replace("../dashboard.html?smart=1");
  } catch (err) {
    if (statusEl) statusEl.textContent = `Sign-in failed: ${err?.message || err}`;
    if (retryEl) retryEl.classList.remove("hidden");
  }
})();
