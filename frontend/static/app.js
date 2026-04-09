/**
 * Spanish Practice — FastAPI client. When hosted separately (e.g. Vercel), set
 * window.__API_BASE__ in api-config.js to the API origin (no trailing slash).
 */

const STORAGE_USER = "sp_username";

const WORD_COUNTS = {
  beginner: { w: 60, r: 100 },
  novice: { w: 120, r: 250 },
  intermediate: { w: 200, r: 400 },
};

const TENSE_OPTS = [
  ["presente_de_indicativo", "Presente de indicativo"],
  ["preterito_perfecto_simple", "Pretérito perfecto simple"],
  ["preterito_imperfecto", "Pretérito imperfecto"],
  ["futuro_simple", "Futuro simple"],
  ["condicional_simple", "Condicional simple"],
];

const GRAMMAR_OPTS = [
  ["gender_agreement", "Gender agreement"],
  ["plurality_agreement", "Plurality agreement"],
  ["por_para_usage", "Por / para"],
  ["indirect_direct_pronoun_usage", "Pronouns"],
  ["verb_subject_conjugation", "Verb conjugation"],
];

const TOPIC_OPTS = [
  ["travel", "Travel"],
  ["school", "School"],
  ["work", "Work"],
  ["culture", "Culture"],
  ["current_events", "Current events"],
  ["emotions", "Emotions"],
  ["relationships", "Relationships"],
];

const DRILL_ORDER = [
  "sentence_completion",
  "translate",
  "error_correction",
  "option_selection",
];

/** @type {{ exercise: object | null, writingPrompt: string | null, readingPrompt: object | null, drills: object | null }} */
const state = {
  exercise: null,
  writingPrompt: null,
  readingPrompt: null,
  drills: null,
};

function getUsername() {
  return sessionStorage.getItem(STORAGE_USER);
}

function setUsername(name) {
  sessionStorage.setItem(STORAGE_USER, name);
}

function clearSession() {
  sessionStorage.removeItem(STORAGE_USER);
}

function setStatus(message, isError) {
  const el = document.getElementById("status");
  if (!message) {
    el.textContent = "";
    el.classList.remove("is-visible", "banner-status--ok", "banner-status--err");
    el.removeAttribute("role");
    return;
  }
  el.textContent = message;
  el.classList.add("is-visible");
  el.classList.toggle("banner-status--ok", !isError);
  el.classList.toggle("banner-status--err", !!isError);
  if (isError) el.setAttribute("role", "alert");
  else el.removeAttribute("role");
}

/**
 * @param {HTMLButtonElement | null} btn
 * @param {string} busyLabel
 * @param {() => Promise<any>} fn
 */
async function withBusy(btn, busyLabel, fn) {
  if (!btn) return fn();
  const label = btn.querySelector(".btn-label");
  const textNode = label || btn;
  const orig = textNode.textContent;
  const spinner = document.createElement("span");
  spinner.className = "btn-spinner";
  spinner.setAttribute("aria-hidden", "true");
  btn.insertBefore(spinner, btn.firstChild);
  btn.disabled = true;
  btn.classList.add("is-busy");
  btn.setAttribute("aria-busy", "true");
  textNode.textContent = busyLabel;
  try {
    return await fn();
  } finally {
    spinner.remove();
    btn.disabled = false;
    btn.classList.remove("is-busy");
    btn.removeAttribute("aria-busy");
    textNode.textContent = orig;
  }
}

function apiBase() {
  const b =
    typeof window !== "undefined" && window.__API_BASE__ != null
      ? String(window.__API_BASE__).trim().replace(/\/+$/, "")
      : "";
  return b;
}

/**
 * @param {string} method
 * @param {string} path
 * @param {object} [body]
 */
async function api(method, path, body) {
  /** @type {RequestInit} */
  const opts = { method };
  if (body !== undefined) {
    opts.headers = { "Content-Type": "application/json" };
    opts.body = JSON.stringify(body);
  }
  const url = path.startsWith("http") ? path : `${apiBase()}${path}`;
  const r = await fetch(url, opts);
  const text = await r.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!r.ok) {
    let msg;
    if (data && typeof data.detail === "string") msg = data.detail;
    else if (Array.isArray(data?.detail))
      msg = data.detail.map((d) => d.msg || JSON.stringify(d)).join("; ");
    else if (typeof data === "string") msg = data;
    else msg = r.statusText || "Request failed";
    throw new Error(msg);
  }
  return data;
}

function exerciseContextFromExercise(ex) {
  const d = ex.difficulty_level;
  const isReading = ex.exercise_type === "reading";
  const wc = WORD_COUNTS[d];
  const word_count = isReading ? wc.r : wc.w;
  return {
    areas_of_focus: ex.areas_of_focus,
    exercise_config: { difficulty: d, word_count },
  };
}

function humanizeKey(key) {
  return String(key)
    .split("_")
    .join(" ");
}

function buildCheckboxGrid(container, options, namePrefix) {
  container.innerHTML = "";
  for (const [value, text] of options) {
    const id = `${namePrefix}-${value}`;
    const labelEl = document.createElement("label");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = value;
    input.id = id;
    input.name = namePrefix;
    labelEl.appendChild(input);
    labelEl.appendChild(document.createTextNode(text));
    container.appendChild(labelEl);
  }
}

function getCheckedValues(namePrefix) {
  return Array.from(
    document.querySelectorAll(`input[name="${namePrefix}"]:checked`),
  ).map((el) => el.value);
}

function showPanel(id) {
  document.getElementById("panel-login").classList.toggle("hidden", id !== "login");
  document.getElementById("panel-exercise").classList.toggle("hidden", id !== "exercise");
  document.getElementById("panel-practice").classList.toggle("hidden", id !== "practice");
  document.getElementById("panel-progress").classList.toggle("hidden", id !== "progress");
}

function updateExerciseUserLabel() {
  const u = getUsername();
  const el = document.getElementById("exercise-user-label");
  if (u) {
    el.hidden = false;
    el.textContent = `Signed in as ${u}`;
  } else {
    el.hidden = true;
  }
}

function rebuildDrillPrefGrid() {
  const axis =
    document.querySelector('input[name="drill-pref-axis"]:checked')?.value ||
    "tenses";
  const wrap = document.getElementById("drill-pref-grid-wrap");
  const opts = axis === "grammar" ? GRAMMAR_OPTS : TENSE_OPTS;
  buildCheckboxGrid(wrap, opts, "drill-pref-item");
}

function syncPreferencePanels() {
  const style = document.querySelector('input[name="style"]:checked').value;
  const box = document.getElementById("preferences-box");
  const standard = document.getElementById("preferences-standard");
  const drillsOnly = document.getElementById("preferences-drills-only");
  if (style !== "preferences") return;
  const type = document.getElementById("ex-type").value;
  const isDrills = type === "drills";
  standard.classList.toggle("hidden", isDrills);
  drillsOnly.classList.toggle("hidden", !isDrills);
  if (isDrills) rebuildDrillPrefGrid();
}

function onStyleChange() {
  const style = document.querySelector('input[name="style"]:checked').value;
  document.getElementById("preferences-box").classList.toggle("hidden", style !== "preferences");
  if (style === "preferences") syncPreferencePanels();
}

async function onLogin(ev) {
  ev.preventDefault();
  setStatus("");
  const username = document.getElementById("login-username").value.trim();
  const key = document.getElementById("login-key").value;
  const newUser = document.getElementById("login-new").checked;
  if (!username) {
    setStatus("Please enter a username.", true);
    return;
  }
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    await withBusy(submitBtn, "Signing in…", () =>
      api("POST", "/user/login", { username, key, new: newUser }),
    );
    setUsername(username);
    setStatus("Signed in. Choose an exercise below.", false);
    updateExerciseUserLabel();
    showPanel("exercise");
  } catch (e) {
    setStatus(e.message, true);
  }
}

function readExerciseFormBody() {
  const username = getUsername();
  const type = document.getElementById("ex-type").value;
  const difficulty = document.getElementById("ex-difficulty").value;
  const style = document.querySelector('input[name="style"]:checked').value;
  let preferences = null;
  if (style === "preferences") {
    if (type === "drills") {
      const axis =
        document.querySelector('input[name="drill-pref-axis"]:checked')?.value ||
        "tenses";
      const selected = getCheckedValues("drill-pref-item");
      if (selected.length === 0) {
        throw new Error(
          axis === "grammar"
            ? "Select at least one grammar focus for drills."
            : "Select at least one tense for drills.",
        );
      }
      preferences =
        axis === "grammar"
          ? {
              focus_tenses: null,
              focus_grammar: selected,
              focus_topics: null,
            }
          : {
              focus_tenses: selected,
              focus_grammar: null,
              focus_topics: null,
            };
    } else {
      preferences = {
        focus_tenses: getCheckedValues("pref-tense"),
        focus_grammar: getCheckedValues("pref-grammar"),
        focus_topics: getCheckedValues("pref-topic"),
      };
      const n =
        preferences.focus_tenses.length +
        preferences.focus_grammar.length +
        preferences.focus_topics.length;
      if (n === 0) {
        throw new Error("Select at least one tense, grammar area, or topic.");
      }
    }
  }
  return { username, type, difficulty, style, preferences };
}

async function onExerciseSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  let body;
  try {
    body = readExerciseFormBody();
  } catch (e) {
    setStatus(e.message, true);
    return;
  }
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    await withBusy(submitBtn, "Starting…", () =>
      api("POST", "/exercise/generate", body).then((res) => {
        state.exercise = res.exercise;
        state.writingPrompt = null;
        state.readingPrompt = null;
        state.drills = null;
        showPanel("practice");
        return runGenerateForCurrentExercise();
      }),
    );
    setStatus("Ready — your exercise is below.", false);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function showPracticeLoading(message) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const wrap = document.createElement("div");
  wrap.className = "loading-inline";
  const sp = document.createElement("span");
  sp.className = "btn-spinner";
  sp.setAttribute("aria-hidden", "true");
  wrap.appendChild(sp);
  wrap.appendChild(document.createTextNode(message));
  root.appendChild(wrap);
}

async function runGenerateForCurrentExercise() {
  const ex = state.exercise;
  const u = getUsername();
  if (!ex || !u) return;
  showPracticeLoading("Building your exercise — this can take a moment…");
  const ctx = exerciseContextFromExercise(ex);
  try {
    if (ex.exercise_type === "writing") {
      const res = await api("POST", "/writing/generate", {
        username: u,
        exercise_context: ctx,
      });
      state.writingPrompt = res.prompt;
      renderWritingPractice();
    } else if (ex.exercise_type === "reading") {
      const res = await api("POST", "/reading/generate", {
        username: u,
        exercise_context: ctx,
      });
      state.readingPrompt = res.prompt;
      renderReadingPractice();
    } else if (ex.exercise_type === "drills") {
      const res = await api("POST", "/drills/generate", {
        username: u,
        exercise_context: ctx,
      });
      state.drills = res.prompt;
      renderDrillsPractice();
    } else {
      const root = document.getElementById("practice-root");
      root.innerHTML = `<p class="passage">Unknown exercise type: ${ex.exercise_type}</p>`;
    }
  } catch (e) {
    document.getElementById("practice-root").innerHTML = "";
    setStatus(e.message, true);
  }
}

function renderWritingPractice() {
  const root = document.getElementById("practice-root");
  const prompt = state.writingPrompt;
  root.innerHTML = "";
  const p = document.createElement("p");
  p.className = "passage";
  p.textContent = prompt;
  root.appendChild(p);
  const form = document.createElement("form");
  form.id = "form-writing";
  const lab = document.createElement("label");
  lab.htmlFor = "writing-response";
  lab.textContent = "Your text";
  const ta = document.createElement("textarea");
  ta.id = "writing-response";
  ta.required = true;
  form.appendChild(lab);
  form.appendChild(ta);
  const btn = document.createElement("button");
  btn.type = "submit";
  btn.className = "btn btn-primary";
  btn.innerHTML = '<span class="btn-label">Submit for feedback</span>';
  form.appendChild(btn);
  form.addEventListener("submit", onWritingSubmit);
  root.appendChild(form);
}

async function onWritingSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  const text = document.getElementById("writing-response").value;
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    const res = await withBusy(submitBtn, "Getting feedback…", () =>
      api("POST", "/writing/submit", {
        username: getUsername(),
        prompt: state.writingPrompt,
        user_response: text,
      }),
    );
    setStatus("Feedback is ready below.", false);
    showResultsWriting(res);
  } catch (e) {
    setStatus(e.message, true);
  }
}

/**
 * @param {HTMLElement} container
 * @param {object} edit
 */
function appendEditCard(container, edit) {
  if (!edit || typeof edit !== "object") return;
  const card = document.createElement("div");
  card.className = "correction-card";
  const o = edit.original_text ?? "";
  const c = edit.corrected_text ?? "";
  const r = edit.reason ?? "";
  const diff = document.createElement("p");
  diff.className = "diff-line";
  diff.innerHTML = `<del>${escapeHtml(o)}</del> → <ins>${escapeHtml(c)}</ins>`;
  card.appendChild(diff);
  if (r) {
    const reason = document.createElement("p");
    reason.className = "reason";
    reason.textContent = r;
    card.appendChild(reason);
  }
  container.appendChild(card);
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/**
 * @param {HTMLElement} parent
 * @param {string} title
 * @param {Record<string, object[]> | object[] | null | undefined} data
 */
function appendEditSection(parent, title, data) {
  if (data == null) return;
  if (Array.isArray(data)) {
    if (data.length === 0) return;
    const sec = document.createElement("div");
    sec.className = "correction-section";
    const h = document.createElement("p");
    h.className = "correction-section-title";
    h.textContent = title;
    sec.appendChild(h);
    for (const item of data) appendEditCard(sec, item);
    parent.appendChild(sec);
    return;
  }
  if (typeof data === "object") {
    const keys = Object.keys(data);
    if (keys.length === 0) return;
    const sec = document.createElement("div");
    sec.className = "correction-section";
    const h = document.createElement("p");
    h.className = "correction-section-title";
    h.textContent = title;
    sec.appendChild(h);
    for (const k of keys) {
      const edits = data[k];
      if (!Array.isArray(edits) || edits.length === 0) continue;
      const sub = document.createElement("p");
      sub.className = "sub-label";
      sub.style.marginTop = "0.65rem";
      sub.textContent = humanizeKey(k);
      sec.appendChild(sub);
      for (const item of edits) appendEditCard(sec, item);
    }
    parent.appendChild(sec);
  }
}

function showResultsWriting(res) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const fb = document.createElement("div");
  fb.className = "feedback-block";
  const hSum = document.createElement("h3");
  hSum.textContent = "Summary";
  fb.appendChild(hSum);
  const sum = res.summarised_correction;
  fb.appendChild(
    elBlock(
      [
        sum.general_feedback,
        "",
        sum.tense_edits,
        "",
        sum.grammar_edits,
        "",
        sum.topic_edits,
      ].join("\n"),
    ),
  );

  const dc = res.detailed_correction;
  const hCorr = document.createElement("h3");
  hCorr.textContent = "Corrected version";
  fb.appendChild(hCorr);
  fb.appendChild(elBlock(dc.corrected_version || ""));

  const hDetail = document.createElement("h3");
  hDetail.textContent = "Corrections in detail";
  fb.appendChild(hDetail);
  const detailWrap = document.createElement("div");
  appendEditSection(detailWrap, "Verb tenses", dc.tense_errors);
  appendEditSection(detailWrap, "Grammar", dc.grammar_errors);
  appendEditSection(detailWrap, "Topic / vocabulary", dc.topic_errors);
  appendEditSection(detailWrap, "Typos & small fixes", dc.typos);
  appendEditSection(detailWrap, "Other", dc.other_mistakes);
  if (!detailWrap.children.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No structured edits were returned — see the summary above.";
    detailWrap.appendChild(empty);
  }
  fb.appendChild(detailWrap);
  root.appendChild(fb);
}

function elBlock(text) {
  const p = document.createElement("p");
  p.className = "passage";
  p.textContent = text;
  return p;
}

function renderReadingPractice() {
  const root = document.getElementById("practice-root");
  const pr = state.readingPrompt;
  root.innerHTML = "";
  const art = document.createElement("p");
  art.className = "passage";
  art.textContent = pr.passage;
  root.appendChild(art);
  const form = document.createElement("form");
  form.id = "form-reading";
  pr.questions.forEach((q, i) => {
    const wrap = document.createElement("div");
    wrap.className = "question-block";
    const lab = document.createElement("label");
    lab.htmlFor = `reading-q-${i}`;
    lab.textContent = `Question ${i + 1}: ${q}`;
    const inp = document.createElement("input");
    inp.type = "text";
    inp.id = `reading-q-${i}`;
    inp.required = true;
    wrap.appendChild(lab);
    wrap.appendChild(inp);
    form.appendChild(wrap);
  });
  const btn = document.createElement("button");
  btn.type = "submit";
  btn.className = "btn btn-primary";
  btn.innerHTML = '<span class="btn-label">Submit answers</span>';
  form.appendChild(btn);
  form.addEventListener("submit", onReadingSubmit);
  root.appendChild(form);
}

async function onReadingSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  const pr = state.readingPrompt;
  const user_response = pr.questions.map((_, i) =>
    document.getElementById(`reading-q-${i}`).value.trim(),
  );
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    const res = await withBusy(submitBtn, "Checking answers…", () =>
      api("POST", "/reading/submit", {
        username: getUsername(),
        user_response,
      }),
    );
    setStatus("Feedback is ready below.", false);
    showResultsReading(res, pr.questions, user_response);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function showResultsReading(res, questions = [], userResponses = []) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const fb = document.createElement("div");
  fb.className = "feedback-block";
  const h = document.createElement("h3");
  h.textContent = "Feedback";
  fb.appendChild(h);
  const corr = res.correction;
  (corr.individual_questions || []).forEach((t, i) => {
    const hq = document.createElement("h4");
    hq.textContent = `Question ${i + 1}`;
    const question = document.createElement("p");
    question.className = "passage";
    question.textContent = `Question: ${questions[i] || ""}`;
    const response = document.createElement("p");
    response.className = "passage";
    response.textContent = `Your response: ${userResponses[i] || ""}`;
    const p = document.createElement("p");
    p.className = "passage";
    p.textContent = `Feedback: ${t}`;
    fb.appendChild(hq);
    fb.appendChild(question);
    fb.appendChild(response);
    fb.appendChild(p);
  });
  const ho = document.createElement("h4");
  ho.textContent = "Overall";
  const g = document.createElement("p");
  g.className = "passage";
  g.textContent = corr.general_feedback;
  fb.appendChild(ho);
  fb.appendChild(g);
  root.appendChild(fb);
}

function renderDrillsPractice() {
  const root = document.getElementById("practice-root");
  const drills = state.drills;
  root.innerHTML = "";
  const form = document.createElement("form");
  form.id = "form-drills";
  for (const dt of DRILL_ORDER) {
    const set = drills.drill_sets[dt];
    if (!set || !set.drills?.length) continue;
    const h = document.createElement("h3");
    h.className = "drill-type-title";
    h.textContent = humanizeKey(dt);
    form.appendChild(h);
    set.drills.forEach((d, i) => {
      const block = document.createElement("div");
      block.className = "question-block";
      const promptP = document.createElement("p");
      promptP.textContent = d.prompt;
      block.appendChild(promptP);
      if (d.options && d.options.length) {
        const ul = document.createElement("ul");
        ul.className = "option-list";
        const name = `drill-${dt}-${i}`;
        d.options.forEach((opt, j) => {
          const li = document.createElement("li");
          const lab = document.createElement("label");
          const radio = document.createElement("input");
          radio.type = "radio";
          radio.name = name;
          radio.value = opt;
          radio.required = true;
          if (j === 0) radio.checked = true;
          lab.appendChild(radio);
          lab.appendChild(document.createTextNode(opt));
          li.appendChild(lab);
          ul.appendChild(li);
        });
        block.appendChild(ul);
      } else {
        const inp = document.createElement("input");
        inp.type = "text";
        inp.required = true;
        inp.id = `drill-input-${dt}-${i}`;
        inp.setAttribute("aria-label", `Answer for: ${d.prompt.slice(0, 80)}`);
        block.appendChild(inp);
      }
      form.appendChild(block);
    });
  }
  const btn = document.createElement("button");
  btn.type = "submit";
  btn.className = "btn btn-primary";
  btn.innerHTML = '<span class="btn-label">Submit drills</span>';
  form.appendChild(btn);
  form.addEventListener("submit", onDrillsSubmit);
  root.appendChild(form);
}

function collectDrillResponses() {
  const drills = state.drills;
  /** @type {Record<string, string[]>} */
  const responses = {};
  for (const dt of DRILL_ORDER) {
    const set = drills.drill_sets[dt];
    if (!set || !set.drills?.length) continue;
    responses[dt] = set.drills.map((_, i) => {
      const name = `drill-${dt}-${i}`;
      const checked = document.querySelector(`input[name="${name}"]:checked`);
      if (checked) return checked.value;
      const inp = document.getElementById(`drill-input-${dt}-${i}`);
      return inp ? inp.value.trim() : "";
    });
  }
  return { responses };
}

async function onDrillsSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  const user_response = collectDrillResponses();
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    const res = await withBusy(submitBtn, "Marking answers…", () =>
      api("POST", "/drills/submit", {
        username: getUsername(),
        user_response,
      }),
    );
    setStatus("Results are ready below.", false);
    showResultsDrills(res);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function showResultsDrills(res) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const fb = document.createElement("div");
  fb.className = "feedback-block";
  const h = document.createElement("h3");
  h.textContent = "Results";
  fb.appendChild(h);
  const md = res.marked_drills;
  for (const set of md.marked_drill_sets || []) {
    const dt = set.drill_type;
    const sub = document.createElement("h4");
    sub.className = "drill-type-title";
    sub.textContent = humanizeKey(dt);
    sub.style.marginTop = "1rem";
    fb.appendChild(sub);
    for (const row of set.marked_drills || []) {
      const div = document.createElement("div");
      div.className = "drill-result-item";
      const badge = document.createElement("span");
      badge.className = row.is_correct ? "badge badge-ok" : "badge badge-no";
      badge.textContent = row.is_correct ? "Correct" : "Review";
      div.appendChild(badge);
      div.appendChild(
        document.createTextNode(` ${row.prompt || ""} — Your answer: "${row.user_response || ""}"`),
      );
      if (row.comment) {
        const c = document.createElement("p");
        c.className = "reason";
        c.style.marginTop = "0.35rem";
        c.textContent = row.comment;
        div.appendChild(c);
      }
      fb.appendChild(div);
    }
  }
  if (md.stats) {
    const pill = document.createElement("p");
    pill.className = "stats-pill";
    pill.textContent = `Score: ${md.stats.correct_attempts} / ${md.stats.total_attempts} correct`;
    fb.appendChild(pill);
  }
  root.appendChild(fb);
}

async function onProgressClick() {
  setStatus("");
  const u = getUsername();
  if (!u) return;
  const btn = document.getElementById("btn-progress");
  try {
    const res = await withBusy(btn, "Loading…", () =>
      api("POST", "/progress/generate", { username: u }),
    );
    renderProgress(res.progress);
    showPanel("progress");
    setStatus("Progress loaded.", false);
  } catch (e) {
    setStatus(e.message, true);
  }
}

/**
 * Same logic as `calculate_score` in src/domain/rules/score.py
 * @param {{ total_attempts?: number, correct_attempts?: number }} stats
 * @returns {number} percentage 0–100
 */
function calculateScorePercent(stats) {
  const total = Number(stats?.total_attempts) || 0;
  if (total === 0) return 0;
  return (Number(stats.correct_attempts) / total) * 100;
}

/**
 * @param {{ total_attempts?: number, correct_attempts?: number }} stats
 */
function formatProgressScore(stats) {
  const p = calculateScorePercent(stats);
  const rounded = Math.round(p * 10) / 10;
  return Number.isInteger(rounded) ? `${rounded}%` : `${rounded.toFixed(1)}%`;
}

function renderProgress(progress) {
  const root = document.getElementById("progress-root");
  root.innerHTML = "";
  root.appendChild(progressTable("Tenses", progress.tenses));
  root.appendChild(progressTable("Grammar", progress.grammar));
  root.appendChild(progressTable("Topics", progress.topics));
}

function progressTable(title, dict) {
  const wrap = document.createElement("div");
  wrap.className = "progress-block";
  const h = document.createElement("h3");
  h.textContent = title;
  wrap.appendChild(h);
  const table = document.createElement("table");
  table.className = "progress-table";
  table.innerHTML =
    "<thead><tr><th>Area</th><th>Score</th></tr></thead>";
  const tb = document.createElement("tbody");
  for (const [k, v] of Object.entries(dict || {})) {
    const tr = document.createElement("tr");
    const td1 = document.createElement("td");
    td1.textContent = humanizeKey(k);
    const td2 = document.createElement("td");
    td2.textContent = formatProgressScore(v);
    td2.className = "progress-score-cell";
    tr.appendChild(td1);
    tr.appendChild(td2);
    tb.appendChild(tr);
  }
  table.appendChild(tb);
  wrap.appendChild(table);
  return wrap;
}

function onBackExercise() {
  state.exercise = null;
  state.writingPrompt = null;
  state.readingPrompt = null;
  state.drills = null;
  document.getElementById("practice-root").innerHTML = "";
  setStatus("");
  showPanel("exercise");
}

function onLogout() {
  clearSession();
  state.exercise = null;
  state.writingPrompt = null;
  state.readingPrompt = null;
  state.drills = null;
  document.getElementById("practice-root").innerHTML = "";
  document.getElementById("progress-root").innerHTML = "";
  setStatus("Logged out.", false);
  showPanel("login");
}

function init() {
  const prefTenses = document.getElementById("pref-tenses");
  const prefGrammar = document.getElementById("pref-grammar");
  const prefTopics = document.getElementById("pref-topics");
  buildCheckboxGrid(prefTenses, TENSE_OPTS, "pref-tense");
  buildCheckboxGrid(prefGrammar, GRAMMAR_OPTS, "pref-grammar");
  buildCheckboxGrid(prefTopics, TOPIC_OPTS, "pref-topic");

  document.getElementById("form-login").addEventListener("submit", onLogin);
  document.getElementById("form-exercise").addEventListener("submit", onExerciseSubmit);
  document.getElementById("btn-logout").addEventListener("click", onLogout);
  document.getElementById("btn-progress").addEventListener("click", onProgressClick);
  document.getElementById("btn-back-exercise").addEventListener("click", onBackExercise);
  document.getElementById("btn-close-progress").addEventListener("click", () => {
    showPanel("exercise");
  });

  document.querySelectorAll('input[name="style"]').forEach((r) => {
    r.addEventListener("change", onStyleChange);
  });

  document.getElementById("ex-type").addEventListener("change", () => {
    syncPreferencePanels();
  });

  document.querySelectorAll('input[name="drill-pref-axis"]').forEach((r) => {
    r.addEventListener("change", rebuildDrillPrefGrid);
  });

  if (getUsername()) {
    updateExerciseUserLabel();
    showPanel("exercise");
  } else {
    showPanel("login");
  }
}

document.addEventListener("DOMContentLoaded", init);
