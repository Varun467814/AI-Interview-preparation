// frontend/js/results.js
// Reads the analysis result from sessionStorage and renders the full results UI.

// ── Animated loading steps ────────────────────────────────────────────────────
const LOADING_STEPS = [
  "Parsing your resume…",
  "Extracting skills and experience…",
  "Analyzing job description…",
  "Running skill gap analysis…",
  "Generating interview questions…",
  "Building your report…",
];

let stepIdx = 0;
const stepEl = document.getElementById("loading-step-text");
const stepInterval = setInterval(() => {
  stepIdx = (stepIdx + 1) % LOADING_STEPS.length;
  if (stepEl) stepEl.textContent = LOADING_STEPS[stepIdx];
}, 900);

// ── Load data ─────────────────────────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
  const raw = sessionStorage.getItem("interviewResult");

  setTimeout(() => {               // slight delay so loader shows
    clearInterval(stepInterval);
    if (!raw) {
      showErrorState();
      return;
    }
    try {
      const data = JSON.parse(raw);
      renderResults(data);
    } catch {
      showErrorState();
    }
  }, 1400);
});

// ── Main render function ───────────────────────────────────────────────────────
function renderResults(data) {
  const overlay  = document.getElementById("loading-overlay");
  const content  = document.getElementById("results-content");

  overlay.style.display  = "none";
  content.style.display  = "block";

  const cp  = data.candidate_profile   || {};
  const jd  = data.jd_analysis          || {};
  const gap = data.skill_gap            || {};
  const qs  = data.interview_questions  || {};

  // ── Hero ─────────────────────────────────────────────────────────────────
  setText("hero-role", `Role: ${data.target_role || jd.role_title || "N/A"}`);
  const badge = document.getElementById("readiness-badge");
  if (badge) badge.textContent = `${gap.readiness_level || "Analysis Complete"}`;

  // ── Summary bar ───────────────────────────────────────────────────────────
  setText("sum-match",     (gap.match_percentage ?? "—") + "%");
  setText("sum-matching",  gap.matching_skills?.length ?? "—");
  setText("sum-missing",   gap.missing_skills?.length  ?? "—");
  setText("sum-questions", qs.total_questions            ?? "—");

  // ── Candidate profile ─────────────────────────────────────────────────────
  setText("p-name",  cp.name  || "Candidate");
  setText("p-email", cp.email || "—");

  const metaEl = document.getElementById("p-meta");
  if (metaEl) {
    const metaItems = [];
    if (cp.phone && cp.phone !== "N/A") metaItems.push(`📞 ${cp.phone}`);
    if (cp.years_of_experience)         metaItems.push(`🗓 ${cp.years_of_experience} yrs exp`);
    if (cp.education?.[0])              metaItems.push(`🎓 ${cp.education[0]}`);
    metaEl.innerHTML = metaItems.map(m => `<span class="profile-chip">${m}</span>`).join("");
  }

  renderChips("p-skills", cp.skills || [], "chip-neutral");

  // ── JD analysis ───────────────────────────────────────────────────────────
  setText("jd-role-sub", `Required experience: ${jd.required_experience_years || 0} years`);
  const respEl = document.getElementById("jd-responsibilities");
  if (respEl) {
    const resps = jd.responsibilities?.length ? jd.responsibilities : ["No responsibilities extracted."];
    respEl.innerHTML = resps.map(r => `<li>${escHtml(r)}</li>`).join("");
  }
  renderChips("jd-keywords", jd.keywords || [], "chip-purple");

  // ── Skill gap ─────────────────────────────────────────────────────────────
  const pct = gap.match_percentage ?? 0;
  const gaugeEl  = document.getElementById("gauge-circle");
  const gaugeBar = document.getElementById("gauge-bar");

  if (gaugeEl)  {
    gaugeEl.textContent = pct + "%";
    // colour based on score
    if (pct >= 80)       gaugeEl.style.background = "linear-gradient(135deg,#16a34a,#22c55e)";
    else if (pct >= 50)  gaugeEl.style.background = "linear-gradient(135deg,#d97706,#f59e0b)";
    else if (pct >= 25)  gaugeEl.style.background = "linear-gradient(135deg,#ea580c,#f97316)";
    else                 gaugeEl.style.background = "linear-gradient(135deg,#dc2626,#ef4444)";
  }
  if (gaugeBar) setTimeout(() => gaugeBar.style.width = pct + "%", 200);

  setText("readiness-level",    gap.readiness_level    || "—");
  setText("recommendation-text", gap.recommendation    || "");

  const matchingEl = gap.matching_skills || [];
  const missingEl  = gap.missing_skills  || [];

  renderChips("matching-skills", matchingEl, "chip-match");
  renderChips("missing-skills",  missingEl,  "chip-missing");

  if (matchingEl.length === 0) show("no-matching");
  if (missingEl.length  === 0) show("no-missing");

  // Experience gap
  if ((gap.experience_gap_years || 0) > 0) {
    const expNote = document.getElementById("exp-gap-note");
    if (expNote) {
      expNote.textContent = `⚠️ Experience gap: You have ${gap.candidate_experience_years} yrs; role requires ${gap.required_experience_years} yrs.`;
      expNote.style.display = "block";
    }
  }

  // ── Interview questions ───────────────────────────────────────────────────
  const diff = qs.difficulty_level || "Beginner";
  const diffWrap = document.getElementById("difficulty-badge-wrap");
  if (diffWrap) {
    const cls = { Advanced: "diff-advanced", Intermediate: "diff-intermediate", Beginner: "diff-beginner" }[diff] || "diff-beginner";
    const icon = { Advanced: "🔥", Intermediate: "⚡", Beginner: "🌱" }[diff] || "🌱";
    diffWrap.innerHTML = `<span class="difficulty-badge ${cls}">${icon} ${diff} Level Questions</span>`;
  }

  renderQuestions("q-technical", "tech-count",  qs.technical       || []);
  renderQuestions("q-hr",        "hr-count",    qs.hr_behavioural  || []);
  renderQuestions("q-project",   "proj-count",  qs.project_based   || []);
  renderQuestions("q-gap",       "gap-count",   qs.skill_gap_bridging || []);

  if (!(qs.skill_gap_bridging?.length)) show("no-gap-qs");

  // ── Download ──────────────────────────────────────────────────────────────
  const dlBtn = document.getElementById("download-btn");
  if (dlBtn) {
    dlBtn.addEventListener("click", () => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `interview-prep-report-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  // ── Tabs ──────────────────────────────────────────────────────────────────
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("panel-" + btn.dataset.tab)?.classList.add("active");
    });
  });
}

// ── Render helpers ────────────────────────────────────────────────────────────
function renderChips(containerId, items, chipClass) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!items.length) { el.innerHTML = '<span style="font-size:.78rem;color:var(--gray-400)">None detected</span>'; return; }
  el.innerHTML = items.map(item => `<span class="chip ${chipClass}">${escHtml(item)}</span>`).join("");
}

function renderQuestions(listId, countId, questions) {
  const list  = document.getElementById(listId);
  const count = document.getElementById(countId);
  if (count) count.textContent = questions.length;
  if (!list) return;

  list.innerHTML = questions.map((q, i) => `
    <li class="q-item">
      <div class="q-num">${i + 1}</div>
      <div class="q-text">${escHtml(q)}</div>
      <button class="q-copy" title="Copy question" onclick="copyQ(this, ${JSON.stringify(q)})">📋</button>
    </li>
  `).join("");
}

function copyQ(btn, text) {
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = "✅";
    btn.classList.add("copied");
    setTimeout(() => { btn.textContent = "📋"; btn.classList.remove("copied"); }, 1800);
  });
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function show(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = "block";
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function showErrorState() {
  document.getElementById("loading-overlay").style.display = "none";
  document.getElementById("error-state").style.display     = "block";
}
