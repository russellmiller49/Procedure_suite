// SMART on FHIR launch entry point.
//
// EHR launch (Epic/Cerner): the EHR opens this page with ?iss=<fhir-base>&launch=<token>.
// Standalone launch (testing/dev): open with no parameters and pick a configured issuer.
// Either way the page validates the issuer against the server allowlist, performs SMART
// discovery, and redirects to the EHR authorization endpoint with PKCE.

import { beginAuthorization, fetchSmartUiConfig } from "./smartClient.js";
import { findIssuerConfig } from "./smartCore.js";

const statusEl = document.getElementById("smartLaunchStatus");
const pickerEl = document.getElementById("smartIssuerPicker");

function setLaunchStatus(message) {
  if (statusEl) statusEl.textContent = String(message || "");
}

function renderIssuerPicker(issuers) {
  if (!pickerEl) return;
  pickerEl.textContent = "";
  const intro = document.createElement("p");
  intro.className = "subtle";
  intro.textContent =
    "No EHR launch parameters detected. Choose an EHR for a standalone session " +
    "(you will be asked to sign in and select a patient):";
  pickerEl.appendChild(intro);
  for (const issuer of issuers) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "primary";
    button.style.margin = "4px 8px 4px 0";
    button.textContent = issuer.name;
    button.addEventListener("click", async () => {
      button.disabled = true;
      setLaunchStatus(`Redirecting to ${issuer.name} sign-in…`);
      try {
        await beginAuthorization({ issuerConfig: issuer });
      } catch (err) {
        button.disabled = false;
        setLaunchStatus(`Could not start authorization: ${err?.message || err}`);
      }
    });
    pickerEl.appendChild(button);
  }
}

async function run() {
  const params = new URLSearchParams(window.location.search);
  const iss = params.get("iss");
  const launch = params.get("launch");

  const config = await fetchSmartUiConfig();
  if (!config.enabled) {
    setLaunchStatus(
      "SMART on FHIR is disabled on this server. Set SMART_ENABLED=1 and configure " +
        "SMART_ISSUERS (see docs/SMART_ON_FHIR.md)."
    );
    return;
  }
  if (Array.isArray(config.config_errors) && config.config_errors.length) {
    console.warn("SMART issuer config errors:", config.config_errors);
  }
  const issuers = Array.isArray(config.issuers) ? config.issuers : [];
  if (!issuers.length) {
    const detail = (config.config_errors || []).join("; ");
    setLaunchStatus(`No SMART issuers are configured on the server.${detail ? ` (${detail})` : ""}`);
    return;
  }

  if (iss) {
    const issuer = findIssuerConfig(issuers, iss);
    if (!issuer) {
      setLaunchStatus(
        `This EHR issuer is not on the server allowlist: ${iss} — configured issuers: ` +
          issuers.map((entry) => entry.name).join(", ")
      );
      return;
    }
    setLaunchStatus(`Redirecting to ${issuer.name} sign-in…`);
    await beginAuthorization({ issuerConfig: issuer, launch });
    return;
  }

  setLaunchStatus("Ready.");
  renderIssuerPicker(issuers);
}

run().catch((err) => {
  setLaunchStatus(`Launch failed: ${err?.message || err}`);
});
