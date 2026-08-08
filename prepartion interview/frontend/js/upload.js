// frontend/js/upload.js
// Handles file upload form, drag-and-drop, and API call to the backend.

const API_URL = "http://127.0.0.1:8000/analyze";

// ── DOM refs ─────────────────────────────────────────────────────────────────
const form      = document.getElementById("upload-form");
const submitBtn = document.getElementById("submit-btn");
const btnText   = document.getElementById("btn-text");
const errorBox  = document.getElementById("error-box");
const errorMsg  = document.getElementById("error-msg");

// ── Drop-zone wiring ──────────────────────────────────────────────────────────
setupDropZone("resume-drop", "resume-file", "resume-fname");
setupDropZone("jd-drop",     "jd-file",     "jd-fname");

function setupDropZone(zoneId, inputId, fnameId) {
  const zone  = document.getElementById(zoneId);
  const input = document.getElementById(inputId);
  const fname = document.getElementById(fnameId);

  input.addEventListener("change", () => showFile(input, zone, fname));

  zone.addEventListener("dragover", (e) => {
    e.preventDefault();
    zone.classList.add("drag-over");
  });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
  zone.addEventListener("drop", (e) => {
    e.preventDefault();
    zone.classList.remove("drag-over");
    if (e.dataTransfer.files.length) {
      // Create a new DataTransfer to set the files on the input
      const dt = new DataTransfer();
      dt.items.add(e.dataTransfer.files[0]);
      input.files = dt.files;
      showFile(input, zone, fname);
    }
  });
}

function showFile(input, zone, fname) {
  if (input.files && input.files[0]) {
    const name = input.files[0].name;
    zone.classList.add("has-file");
    fname.textContent = "✔ " + name;
  }
}

// ── Form submit ────────────────────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideError();
  setLoading(true);

  const formData = new FormData(form);

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unknown server error." }));
      throw new Error(err.detail || `Server error (${res.status})`);
    }

    const data = await res.json();

    // Store result in sessionStorage and navigate to results page
    sessionStorage.setItem("interviewResult", JSON.stringify(data));
    window.location.href = "results.html";

  } catch (err) {
    showError(err.message || "Failed to connect to the backend. Make sure the API server is running.");
    setLoading(false);
  }
});

// ── Helpers ───────────────────────────────────────────────────────────────────
function setLoading(on) {
  if (on) {
    submitBtn.disabled = true;
    btnText.innerHTML  = '<span class="spinner"></span> Analyzing your profile…';
  } else {
    submitBtn.disabled = false;
    btnText.textContent = "🚀 Analyze My Profile";
  }
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorBox.style.display = "block";
}

function hideError() {
  errorBox.style.display = "none";
}
