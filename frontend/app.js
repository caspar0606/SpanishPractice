/**
 * Spanish Practice — minimal client for same-origin FastAPI backend.
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
    el.removeAttribute("role");
    el.classList.remove("info");
    return;
  }
  el.textContent = message;
  el.classList.toggle("info", !isError);
  if (isError) el.setAttribute("role", "alert");
  else el.removeAttribute("role");
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
  const r = await fetch(path, opts);
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

function buildCheckboxGrid(containerId, options, namePrefix) {
  const root = document.getElementById(containerId);
  root.innerHTML = "";
  for (const [value, label] of options) {
    const id = `${namePrefix}-${value}`;
    const labelEl = document.createElement("label");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = value;
    input.id = id;
    input.name = namePrefix;
    labelEl.appendChild(input);
    labelEl.appendChild(document.createTextNode(label));
    root.appendChild(labelEl);
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
  try {
    await api("POST", "/user/login", { username, key, new: newUser });
    setUsername(username);
    setStatus("Signed in successfully.");
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
      throw new Error("Select at least one tense, grammar area, or topic for preferences.");
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
  try {
    const res = await api("POST", "/exercise/generate", body);
    state.exercise = res.exercise;
    state.writingPrompt = null;
    state.readingPrompt = null;
    state.drills = null;
    showPanel("practice");
    await runGenerateForCurrentExercise();
  } catch (e) {
    setStatus(e.message, true);
  }
}

async function runGenerateForCurrentExercise() {
  const ex = state.exercise;
  const u = getUsername();
  if (!ex || !u) return;
  const root = document.getElementById("practice-root");
  root.innerHTML = "<p>Generating…</p>";
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
      root.innerHTML = `<p>Unknown exercise type: ${ex.exercise_type}</p>`;
    }
  } catch (e) {
    root.innerHTML = "";
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
  btn.textContent = "Submit for feedback";
  form.appendChild(btn);
  form.addEventListener("submit", onWritingSubmit);
  root.appendChild(form);
}

async function onWritingSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  const text = document.getElementById("writing-response").value;
  try {
    const res = await api("POST", "/writing/submit", {
      username: getUsername(),
      prompt: state.writingPrompt,
      user_response: text,
    });
    showResultsWriting(res);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function showResultsWriting(res) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const fb = document.createElement("div");
  fb.className = "feedback-block";
  fb.innerHTML = "<h3>Summary</h3>";
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
  fb.appendChild(document.createElement("h3")).textContent = "Detailed correction";
  fb.appendChild(elBlock(res.detailed_correction.corrected_version));
  const pre = document.createElement("pre");
  pre.className = "json-out";
  pre.textContent = JSON.stringify(res.detailed_correction, null, 2);
  fb.appendChild(document.createElement("h3")).textContent = "Structured details (JSON)";
  fb.appendChild(pre);
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
  btn.textContent = "Submit answers";
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
  try {
    const res = await api("POST", "/reading/submit", {
      username: getUsername(),
      user_response,
    });
    showResultsReading(res);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function showResultsReading(res) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const fb = document.createElement("div");
  fb.className = "feedback-block";
  fb.innerHTML = "<h3>Feedback</h3>";
  const corr = res.correction;
  (corr.individual_questions || []).forEach((t, i) => {
    const h = document.createElement("h4");
    h.textContent = `Question ${i + 1}`;
    const p = document.createElement("p");
    p.className = "passage";
    p.textContent = t;
    fb.appendChild(h);
    fb.appendChild(p);
  });
  const g = document.createElement("p");
  g.className = "passage";
  g.textContent = corr.general_feedback;
  fb.appendChild(document.createElement("h3")).textContent = "Overall";
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
  btn.textContent = "Submit drills";
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
  try {
    const res = await api("POST", "/drills/submit", {
      username: getUsername(),
      user_response,
    });
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
  fb.innerHTML = "<h3>Results</h3>";
  const md = res.marked_drills;
  const pre = document.createElement("pre");
  pre.className = "json-out";
  pre.textContent = JSON.stringify(md, null, 2);
  fb.appendChild(pre);
  if (md.stats) {
    const p = document.createElement("p");
    p.className = "passage";
    p.textContent = `Correct: ${md.stats.correct_attempts} / ${md.stats.total_attempts}`;
    fb.appendChild(p);
  }
  root.appendChild(fb);
}

async function onProgressClick() {
  setStatus("");
  const u = getUsername();
  if (!u) return;
  try {
    const res = await api("POST", "/progress/generate", { username: u });
    renderProgress(res.progress);
    showPanel("progress");
  } catch (e) {
    setStatus(e.message, true);
  }
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
  wrap.style.marginBottom = "1.25rem";
  const h = document.createElement("h3");
  h.textContent = title;
  h.style.fontSize = "1rem";
  wrap.appendChild(h);
  const table = document.createElement("table");
  table.style.width = "100%";
  table.style.borderCollapse = "collapse";
  table.innerHTML =
    "<thead><tr><th style='text-align:left;padding:0.35rem'>Area</th><th style='text-align:right;padding:0.35rem'>Attempts</th><th style='text-align:right;padding:0.35rem'>Correct</th></tr></thead>";
  const tb = document.createElement("tbody");
  for (const [k, v] of Object.entries(dict || {})) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td style='border-top:1px solid var(--border);padding:0.35rem'>${humanizeKey(
      k,
    )}</td><td style='border-top:1px solid var(--border);text-align:right;padding:0.35rem'>${v.total_attempts}</td><td style='border-top:1px solid var(--border);text-align:right;padding:0.35rem'>${v.correct_attempts}</td>`;
    tb.appendChild(tr);
  }
  table.appendChild(tb);
  wrap.appendChild(table);
  return wrap;
}

function onStyleChange() {
  const style = document.querySelector('input[name="style"]:checked').value;
  document.getElementById("preferences-box").classList.toggle("hidden", style !== "preferences");
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
  setStatus("Logged out.");
  showPanel("login");
}

function init() {
  buildCheckboxGrid("pref-tenses", TENSE_OPTS, "pref-tense");
  buildCheckboxGrid("pref-grammar", GRAMMAR_OPTS, "pref-grammar");
  buildCheckboxGrid("pref-topics", TOPIC_OPTS, "pref-topic");

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

  if (getUsername()) {
    updateExerciseUserLabel();
    showPanel("exercise");
  } else {
    showPanel("login");
  }
}

document.addEventListener("DOMContentLoaded", init);
