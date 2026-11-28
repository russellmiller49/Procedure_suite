// EHR (SMART on FHIR) panel for the main dashboard (index.html).
//
// Renders only when a SMART session exists in this tab (i.e., the user arrived via
// /ui/smart/launch.html from Epic/Cerner or a sandbox). Shows the launch patient,
// lists that patient's clinical notes, and loads a selected note into the editor
// through hooks provided by app.js — after which the normal client-side PHI
// detect -> redact -> submit workflow applies unchanged.
//
// All EHR data rendered here stays in the browser. DOM is built with
// createElement/textContent only (never innerHTML) since values are PHI and
// remote-controlled.

import {
  clearSmartSession,
  fetchNoteAttachmentContent,
  fetchPatientContext,
  getSmartSession,
  listClinicalNotes,
} from "./smartClient.js";
import { noteMatchesEncounter, pickBestAttachment } from "./smartCore.js";

function describeFhirError(err) {
  if (err?.status === 401) {
    return "EHR session expired or unauthorized — relaunch from the EHR (or Disconnect).";
  }
  return String(err?.message || err || "unknown error");
}

function appendMeta(parent, label, value) {
  if (!value) return;
  const span = document.createElement("span");
  const strong = document.createElement("strong");
  strong.textContent = `${label}: `;
  span.appendChild(strong);
  span.appendChild(document.createTextNode(value));
  span.style.marginRight = "14px";
  parent.appendChild(span);
}

function renderBanner(bannerEl, session, patient) {
  if (!bannerEl) return;
  bannerEl.textContent = "";
  const line = document.createElement("div");
  appendMeta(line, "EHR", session.issuerName || session.iss);
  if (patient) {
    appendMeta(line, "Patient", patient.name);
    appendMeta(line, "DOB", patient.birthDate);
    appendMeta(line, "Sex", patient.gender);
    appendMeta(line, "MRN", patient.mrn);
  } else if (session.patientId) {
    appendMeta(line, "Patient", `#${session.patientId} (loading details…)`);
  }
  if (session.userDisplay) appendMeta(line, "User", session.userDisplay);
  bannerEl.appendChild(line);

  const notice = document.createElement("div");
  notice.className = "subtle";
  notice.textContent =
    "EHR context and note text stay in this browser. The coding server receives only " +
    "de-identified text after you apply redactions.";
  bannerEl.appendChild(notice);
}

export async function initSmartEhrPanel(hooks = {}) {
  const card = document.getElementById("smartEhrCard");
  if (!card) return;
  const session = getSmartSession();
  if (!session) return; // no EHR launch in this tab; card stays hidden

  const bannerEl = document.getElementById("smartPatientBanner");
  const statusEl = document.getElementById("smartEhrStatus");
  const notesHost = document.getElementById("smartNotesHost");
  const loadBtn = document.getElementById("smartLoadNotesBtn");
  const disconnectBtn = document.getElementById("smartDisconnectBtn");

  card.classList.remove("hidden");
  const setPanelStatus = (message) => {
    if (statusEl) statusEl.textContent = String(message || "");
  };

  renderBanner(bannerEl, session, null);
  fetchPatientContext()
    .then((patient) => renderBanner(bannerEl, session, patient))
    .catch((err) => setPanelStatus(`Could not load patient details: ${describeFhirError(err)}`));

  async function handleLoadNote(note, button) {
    const attachment = pickBestAttachment(note.attachments);
    if (!attachment) {
      setPanelStatus(`"${note.title}" has no retrievable content attachment.`);
      return;
    }
    button.disabled = true;
    setPanelStatus(`Fetching "${note.title}" from ${session.issuerName}…`);
    try {
      const content = await fetchNoteAttachmentContent(attachment);
      if (content.kind === "pdf") {
        if (typeof hooks.insertPdfBytes !== "function") {
          throw new Error("PDF insertion is unavailable in this build");
        }
        setPanelStatus("PDF attachment — running local (in-browser) extraction…");
        await hooks.insertPdfBytes(content.bytes, `${note.title || "ehr_note"}.pdf`);
        setPanelStatus("PDF note extracted locally. Review the text, then Run Detection.");
      } else {
        if (typeof hooks.insertNoteText !== "function") {
          throw new Error("Editor insertion is unavailable in this build");
        }
        hooks.insertNoteText(content.text);
        setPanelStatus(
          content.bestEffort
            ? "Note loaded (RTF converted best-effort — verify formatting), then Run Detection."
            : "Note loaded into the editor. Review, then Run Detection."
        );
      }
    } catch (err) {
      setPanelStatus(`Failed to load note: ${describeFhirError(err)}`);
    } finally {
      button.disabled = false;
    }
  }

  function renderNotesTable(notes) {
    if (!notesHost) return;
    notesHost.textContent = "";
    if (!notes.length) {
      const empty = document.createElement("div");
      empty.className = "subtle";
      empty.textContent = "No clinical notes found for this patient.";
      notesHost.appendChild(empty);
      return;
    }
    const table = document.createElement("table");
    table.className = "result-table";
    const thead = document.createElement("thead");
    const headRow = document.createElement("tr");
    for (const label of ["Date", "Document", "Status", ""]) {
      const th = document.createElement("th");
      th.textContent = label;
      headRow.appendChild(th);
    }
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    for (const note of notes) {
      const row = document.createElement("tr");

      const dateCell = document.createElement("td");
      dateCell.textContent = note.date ? note.date.slice(0, 10) : "—";
      row.appendChild(dateCell);

      const docCell = document.createElement("td");
      const title = document.createElement("div");
      title.textContent = note.title;
      docCell.appendChild(title);
      const subtitleParts = [note.typeText, note.categoryText].filter(
        (part, idx, arr) => part && part !== note.title && arr.indexOf(part) === idx
      );
      if (noteMatchesEncounter(note, session.encounterId)) {
        subtitleParts.unshift("this encounter");
      }
      if (subtitleParts.length) {
        const subtitle = document.createElement("div");
        subtitle.className = "subtle";
        subtitle.textContent = subtitleParts.join(" · ");
        docCell.appendChild(subtitle);
      }
      row.appendChild(docCell);

      const statusCell = document.createElement("td");
      statusCell.textContent = [note.status, note.docStatus].filter(Boolean).join(" / ") || "—";
      row.appendChild(statusCell);

      const actionCell = document.createElement("td");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "secondary";
      button.textContent = "Load";
      button.addEventListener("click", () => handleLoadNote(note, button));
      actionCell.appendChild(button);
      row.appendChild(actionCell);

      tbody.appendChild(row);
    }
    table.appendChild(tbody);
    notesHost.appendChild(table);
  }

  async function loadNotes() {
    if (loadBtn) loadBtn.disabled = true;
    setPanelStatus(`Loading clinical notes from ${session.issuerName}…`);
    try {
      const notes = await listClinicalNotes();
      renderNotesTable(notes);
      setPanelStatus(
        notes.length
          ? `Showing ${notes.length} most recent document${notes.length === 1 ? "" : "s"}.`
          : "The EHR returned no documents for this patient."
      );
    } catch (err) {
      setPanelStatus(`Could not list notes: ${describeFhirError(err)}`);
    } finally {
      if (loadBtn) loadBtn.disabled = false;
    }
  }

  if (loadBtn) loadBtn.addEventListener("click", loadNotes);
  if (disconnectBtn) {
    disconnectBtn.addEventListener("click", () => {
      clearSmartSession();
      card.classList.add("hidden");
    });
  }

  if (new URLSearchParams(window.location.search).get("smart") === "1") {
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  await loadNotes();
}
