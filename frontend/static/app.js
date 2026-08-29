/**
 * Spanish Practice — FastAPI client. When hosted separately (e.g. Vercel), set
 * window.__API_BASE__ in api-config.js to the API origin (no trailing slash).
 */

const STORAGE_USER = "sp_username";

/** Gloss for each internal band. Learners see a 0–8 number, not A1/B2. */
const BAND_LABELS = {
  A1: "first words and phrases",
  "A1.5": "getting by with the basics",
  A2: "basic conversational Spanish",
  "A2.5": "confident with the basics",
  B1: "solid conversational Spanish",
  "B1.5": "comfortable in most everyday situations",
  B2: "upper intermediate",
};

const BAND_TO_LEVEL = {
  A1: 2,
  "A1.5": 3,
  A2: 4,
  "A2.5": 5,
  B1: 6,
  "B1.5": 7,
  B2: 8,
};

const PROGRESS_UNLOCK_EXERCISES = 3;

function displayLevel(band) {
  if (band == null || band === "") return "";
  if (typeof band === "number") return band;
  if (BAND_TO_LEVEL[band] != null) return BAND_TO_LEVEL[band];
  const asNumber = Number(band);
  return Number.isFinite(asNumber) ? asNumber : "";
}

function levelWithGloss(level, gloss) {
  if (level === "" || level == null) return gloss || "";
  return gloss ? `${level} — ${gloss}` : String(level);
}

function bandLabel(band) {
  if (!band) return "";
  return BAND_LABELS[band] || String(band);
}

/**
 * Turns a week count into something a person can picture. Long goals read
 * better in months or years than as "roughly 120 weeks".
 */
function humanizeDuration(weeks) {
  if (!weeks || weeks < 1) return "";
  if (weeks < 9) return `about ${Math.round(weeks)} week${Math.round(weeks) === 1 ? "" : "s"}`;
  if (weeks < 52) {
    const months = Math.round(weeks / 4.35);
    return `about ${months} month${months === 1 ? "" : "s"}`;
  }
  const years = weeks / 52;
  const rounded = years < 2 ? Math.round(years * 2) / 2 : Math.round(years);
  return `about ${rounded} year${rounded === 1 ? "" : "s"}`;
}

const TENSE_OPTS = [
  ["presente_de_indicativo", "Present tense"],
  ["preterito_perfecto_simple", "Past tense (finished actions)"],
  ["preterito_imperfecto", "Past tense (used to / was doing)"],
  ["futuro_simple", "Future tense (will)"],
  ["condicional_simple", "Conditional (would)"],
];

const GRAMMAR_OPTS = [
  ["gender_agreement", "Masculine and feminine agreement"],
  ["plurality_agreement", "Singular and plural agreement"],
  ["por_para_usage", "Choosing between por and para"],
  ["indirect_direct_pronoun_usage", "Object pronouns (me, te, lo, le)"],
  ["verb_subject_conjugation", "Matching verbs to their subject"],
];

const TOPIC_OPTS = [
  ["travel", "Travel"],
  ["school", "School and study"],
  ["work", "Work"],
  ["culture", "Culture"],
  ["current_events", "News and current events"],
  ["emotions", "Feelings and opinions"],
  ["relationships", "Family and relationships"],
];

/** Preferred display order; keys must match backend `DrillTypes` (`src/domain/enums.py`). */
const DRILL_ORDER = [
  "sentence_completion",
  "translation",
  "error_correction",
  "option_selection",
];

/** Short line shown under the progress count for each drill step. */
const DRILL_STEP_BLURB = {
  sentence_completion: "fill the gap in each sentence.",
  translation: "translate each prompt into Spanish.",
  error_correction: "fix the mistake in each sentence.",
  option_selection: "choose the best answer for each question.",
};

/**
 * Drill types actually present in the API payload, ordered by DRILL_ORDER then alphabetically.
 * Does not assume the first type or a fixed key set — uses `drill_sets` keys from the server.
 * @param {Record<string, { drills?: unknown[] }> | undefined} drillSets
 */
function orderedDrillKeysWithDrills(drillSets) {
  if (!drillSets || typeof drillSets !== "object") return [];
  const keys = Object.keys(drillSets).filter((k) => drillSets[k]?.drills?.length);
  const rank = new Map(DRILL_ORDER.map((k, i) => [k, i]));
  return keys.sort((a, b) => {
    const ra = rank.has(a) ? rank.get(a) : DRILL_ORDER.length;
    const rb = rank.has(b) ? rank.get(b) : DRILL_ORDER.length;
    if (ra !== rb) return ra - rb;
    return String(a).localeCompare(String(b));
  });
}

/**
 * @param {Record<string, { marked_drills?: unknown[] }>} setsByType
 */
function orderedDrillKeysWithMarked(setsByType) {
  if (!setsByType || typeof setsByType !== "object") return [];
  const keys = Object.keys(setsByType).filter(
    (k) => setsByType[k]?.marked_drills?.length,
  );
  const rank = new Map(DRILL_ORDER.map((k, i) => [k, i]));
  return keys.sort((a, b) => {
    const ra = rank.has(a) ? rank.get(a) : DRILL_ORDER.length;
    const rb = rank.has(b) ? rank.get(b) : DRILL_ORDER.length;
    if (ra !== rb) return ra - rb;
    return String(a).localeCompare(String(b));
  });
}

/** @type {{ exercise: object | null, writingPrompt: string | null, readingPrompt: object | null, drills: object | null, listeningPrompt: object | null, speakingPrompt: string | null, placementForm: object | null, plan: object | null, recommendations: object[] | null, vocabReview: object[] | null }} */
const state = {
  exercise: null,
  writingPrompt: null,
  readingPrompt: null,
  drills: null,
  listeningPrompt: null,
  speakingPrompt: null,
  placementForm: null,
  plan: null,
  recommendations: null,
  vocabReview: null,
};

const PERSON_ORDER = ["yo", "tú", "él/ella", "nosotros", "vosotros", "ellos/ellas"];

const STORAGE_TUTORIAL_DISMISSED = "sp_tutorial_dismissed";

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

const WALKTHROUGH_STEPS = [
  {
    title: "Step 1 — Today’s four",
    text: "Each day, do one writing, reading, listening, and speaking session. Tap a card to start. A ticked card is done until tomorrow.",
  },
  {
    title: "Step 2 — Keep learning",
    text: "Look up a word, or open Learn, Ask, and Vocab anytime. They don’t use up today’s four. After the four are done, that’s the place to continue.",
  },
  {
    title: "Step 3 — Extra practice",
    text: "Want another round, or drills? Open Extra practice and pick the type yourself. That’s on top of the daily four, not instead of them.",
  },
  {
    title: "Step 4 — Submit and review",
    text: "Submit your response. The feedback page includes a summary, your original response, a corrected version, and detailed corrections.",
  },
  {
    title: "Step 5 — Focus & progress",
    text: "Use the Focus tab to see what was selected for this exercise. After you have finished a few exercises, My progress appears on the home screen.",
  },
];

let walkthroughIdx = 0;
let walkthroughAllowed = false;

function helpPanelEl() {
  return document.getElementById("help-panel");
}
function walkthroughOverlayEl() {
  return document.getElementById("walkthrough-overlay");
}

function openHelpPanel() {
  const p = helpPanelEl();
  if (!p) return;
  p.classList.remove("hidden");
}

function closeHelpPanel() {
  const p = helpPanelEl();
  if (!p) return;
  p.classList.add("hidden");
}

function isTutorialDismissed() {
  return localStorage.getItem(STORAGE_TUTORIAL_DISMISSED) === "true";
}

function setTutorialDismissed(isDismissed) {
  localStorage.setItem(STORAGE_TUTORIAL_DISMISSED, isDismissed ? "true" : "false");
}

function renderWalkthroughStep() {
  const stepEl = document.getElementById("walkthrough-step");
  const textEl = document.getElementById("walkthrough-text");
  const backBtn = document.getElementById("walkthrough-back");
  const nextBtn = document.getElementById("walkthrough-next");
  if (!stepEl || !textEl || !backBtn || !nextBtn) return;
  const step = WALKTHROUGH_STEPS[walkthroughIdx] || WALKTHROUGH_STEPS[0];
  stepEl.textContent = step.title;
  textEl.textContent = step.text;
  backBtn.disabled = walkthroughIdx === 0;
  nextBtn.querySelector(".btn-label").textContent =
    walkthroughIdx === WALKTHROUGH_STEPS.length - 1 ? "Finish" : "Next";
}

function openWalkthrough() {
  if (!walkthroughAllowed) return;
  const o = walkthroughOverlayEl();
  if (!o) return;
  closeHelpPanel();
  walkthroughIdx = 0;
  renderWalkthroughStep();
  o.classList.remove("hidden");
}

function maybeOfferWalkthrough() {
  if (!walkthroughAllowed || isTutorialDismissed()) return;
  openWalkthrough();
}

function setWalkthroughAllowed(allowed) {
  walkthroughAllowed = !!allowed;
  const helpBtn = document.getElementById("help-walkthrough");
  if (helpBtn) {
    helpBtn.hidden = !walkthroughAllowed;
    helpBtn.classList.toggle("hidden", !walkthroughAllowed);
  }
  if (!walkthroughAllowed) closeWalkthrough();
}

function syncProgressUnlock(completed) {
  const btn = document.getElementById("btn-progress");
  if (!btn) return;
  const hide = (completed || 0) < PROGRESS_UNLOCK_EXERCISES;
  btn.hidden = hide;
  btn.classList.toggle("hidden", hide);
}

function closeWalkthrough() {
  const o = walkthroughOverlayEl();
  if (!o) return;
  const dontShow = document.getElementById("walkthrough-dont-show");
  if (dontShow && dontShow.checked) setTutorialDismissed(true);
  o.classList.add("hidden");
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
  const opts = {
    method,
    mode: "cors",
    credentials: "omit",
    cache: "no-store",
  };
  if (body !== undefined) {
    opts.headers = { "Content-Type": "application/json" };
    opts.body = JSON.stringify(body);
  }
  const url = path.startsWith("http") ? path : `${apiBase()}${path}`;
  let r;
  try {
    r = await fetch(url, opts);
  } catch (e) {
    const msg =
      e instanceof TypeError
        ? "Network error (request failed or was blocked). If the API is slow, the connection may time out — check Railway logs and try again."
        : String(e?.message || e);
    throw new Error(msg);
  }
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

/**
 * Multipart POST (audio uploads). Do not set Content-Type — the browser
 * supplies the boundary.
 * @param {string} path
 * @param {FormData} formData
 */
async function apiForm(path, formData) {
  const url = path.startsWith("http") ? path : `${apiBase()}${path}`;
  let r;
  try {
    r = await fetch(url, {
      method: "POST",
      mode: "cors",
      credentials: "omit",
      cache: "no-store",
      body: formData,
    });
  } catch (e) {
    const msg =
      e instanceof TypeError
        ? "Network error (request failed or was blocked)."
        : String(e?.message || e);
    throw new Error(msg);
  }
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

function mediaUrl(path) {
  if (!path) return "";
  if (/^https?:\/\//i.test(path)) return path;
  return `${apiBase()}${path.startsWith("/") ? path : `/${path}`}`;
}

const WORD_TOKEN = /([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)/;
const WORD_ONLY = /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+$/;
const translateCache = new Map();
let lastWordAnchor = null;

function translateHint() {
  const p = document.createElement("p");
  p.className = "hint";
  p.textContent = "Tap a Spanish word for an English gloss.";
  return p;
}

function renderClickableSpanish(text, className = "passage", tag = "p") {
  const el = document.createElement(tag);
  if (className) el.className = className;
  const raw = text == null ? "" : String(text);
  const parts = raw.split(WORD_TOKEN);
  parts.forEach((part) => {
    if (WORD_ONLY.test(part)) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "word-hit";
      btn.textContent = part;
      btn.addEventListener("click", (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        openWordPopover(btn, part);
      });
      el.appendChild(btn);
    } else if (part) {
      el.appendChild(document.createTextNode(part));
    }
  });
  return el;
}

function wordPopoverEl() {
  return document.getElementById("word-popover");
}

function closeWordPopover() {
  const el = wordPopoverEl();
  if (!el) return;
  el.classList.add("hidden");
  el.innerHTML = "";
}

function positionWordPopover(anchor) {
  const el = wordPopoverEl();
  if (!el || !anchor) return;
  const rect = anchor.getBoundingClientRect();
  const width = el.offsetWidth || 260;
  const height = el.offsetHeight || 120;
  let top = rect.bottom + 8;
  if (top + height > window.innerHeight - 12) {
    top = Math.max(12, rect.top - height - 8);
  }
  let left = rect.left;
  left = Math.min(left, window.innerWidth - width - 12);
  left = Math.max(12, left);
  el.style.top = `${Math.round(top)}px`;
  el.style.left = `${Math.round(left)}px`;
}

async function fetchTranslation(word) {
  const key = String(word).toLowerCase();
  if (translateCache.has(key)) return translateCache.get(key);
  const data = await api("GET", `/translate/word?q=${encodeURIComponent(word)}`);
  translateCache.set(key, data);
  return data;
}

function renderGlossInto(el, data, options = {}) {
  el.innerHTML = "";
  if (options.showClose) {
    const close = document.createElement("button");
    close.type = "button";
    close.className = "word-popover-close";
    close.setAttribute("aria-label", "Close translation");
    close.textContent = "×";
    close.addEventListener("click", closeWordPopover);
    el.appendChild(close);
  }

  if (!data?.found) {
    const p = document.createElement("p");
    p.className = "hint";
    p.textContent = data?.suggestions?.length
      ? "No exact match. Try:"
      : `No gloss for “${data?.query || "that word"}”.`;
    el.appendChild(p);
    const seen = new Set();
    const query = String(data?.query || "").toLowerCase();
    (data?.suggestions || []).forEach((suggestion) => {
      const label = String(suggestion || "").trim();
      const key = label.toLowerCase();
      if (!label || seen.has(key) || key === query) return;
      seen.add(key);
      if (seen.size > 6) return;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "lesson-chip";
      btn.textContent = label;
      btn.addEventListener("click", (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        if (typeof options.onSuggestion === "function") options.onSuggestion(label);
      });
      el.appendChild(btn);
    });
    return;
  }

  (data.entries || []).forEach((entry) => {
    const glosses = (entry.glosses || []).map((g) => String(g).trim()).filter(Boolean);
    const h = document.createElement("p");
    h.className = "word-popover-head";
    h.textContent = entry.headword || data.query;
    el.appendChild(h);
    if (entry.part_of_speech) {
      const pos = document.createElement("p");
      pos.className = "word-popover-pos";
      pos.textContent = entry.part_of_speech;
      el.appendChild(pos);
    }
    if (!glosses.length) return;
    const ul = document.createElement("ul");
    ul.className = "word-popover-senses";
    glosses.forEach((gloss) => {
      const li = document.createElement("li");
      li.textContent = gloss;
      ul.appendChild(li);
    });
    el.appendChild(ul);
  });
}

function renderWordPopover(el, data) {
  renderGlossInto(el, data, {
    showClose: true,
    onSuggestion: (label) => openWordPopover(lastWordAnchor || el, label),
  });
}

async function lookupWord(word, input) {
  const q = String(word || "").trim();
  const out = document.getElementById("lookup-result");
  if (!out) return;
  if (!q) {
    out.hidden = true;
    out.innerHTML = "";
    return;
  }
  out.hidden = false;
  out.innerHTML = `<p class="hint">Looking up ${escapeHtml(q)}…</p>`;
  if (input) input.value = q;
  try {
    const data = await fetchTranslation(q);
    renderGlossInto(out, data, { onSuggestion: (label) => lookupWord(label, input) });
  } catch (e) {
    out.innerHTML = `<p class="hint">${escapeHtml(e.message)}</p>`;
  }
}

async function onLookupSubmit(ev) {
  ev.preventDefault();
  const input = document.getElementById("lookup-word");
  await lookupWord(input?.value || "", input);
}

async function openWordPopover(anchor, word) {
  const el = wordPopoverEl();
  if (!el) return;
  lastWordAnchor = anchor && anchor !== el ? anchor : lastWordAnchor;
  const pin = lastWordAnchor || el;
  el.classList.remove("hidden");
  el.innerHTML = `<p class="hint">Looking up ${escapeHtml(word)}…</p>`;
  positionWordPopover(pin);
  try {
    const data = await fetchTranslation(word);
    renderWordPopover(el, data);
    positionWordPopover(pin);
  } catch (e) {
    el.innerHTML = `<p class="hint">${escapeHtml(e.message)}</p>`;
    positionWordPopover(pin);
  }
}

function humanizeKey(key) {
  return String(key)
    .split("_")
    .join(" ");
}

/** e.g. sentence_completion → "Sentence completion" (for UI section titles). */
function humanizeKeyTitle(key) {
  return String(key)
    .split("_")
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

/** Fisher–Yates shuffle (copy). */
function shuffleArray(items) {
  const a = items.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
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

function labelFromOpts(opts, key) {
  const hit = opts.find(([value]) => value === key);
  return hit ? hit[1] : humanizeKeyTitle(key);
}

function focusChipRow() {
  const wrap = document.createElement("div");
  wrap.className = "focus-chip-row";
  const caption = document.createElement("span");
  caption.className = "focus-chip-caption";
  caption.textContent = "Your focus";
  wrap.appendChild(caption);

  const focus = state.exercise?.areas_of_focus || {};
  const chips = [
    ...(focus.focus_tenses || []).map((k) => labelFromOpts(TENSE_OPTS, k)),
    ...(focus.focus_grammar || []).map((k) => labelFromOpts(GRAMMAR_OPTS, k)),
    ...(focus.focus_topics || []).map((k) => labelFromOpts(TOPIC_OPTS, k)),
  ].filter((label) => label && !["Tenses", "Grammar", "Topics"].includes(label));

  if (!chips.length) {
    wrap.hidden = true;
    return wrap;
  }
  chips.forEach((label) => {
    const chip = document.createElement("span");
    chip.className = "focus-chip";
    chip.textContent = label;
    wrap.appendChild(chip);
  });
  return wrap;
}

function rebuildDrillPrefGrid() {
  const axis =
    document.querySelector('input[name="drill-pref-axis"]:checked')?.value ||
    "tenses";
  const wrap = document.getElementById("drill-pref-grid-wrap");
  const opts = axis === "grammar" ? GRAMMAR_OPTS : TENSE_OPTS;
  buildCheckboxGrid(wrap, opts, "drill-pref-item");
}

const PANELS = [
  "login",
  "goals",
  "placement",
  "exercise",
  "practice",
  "progress",
  "learn",
  "chat",
  "vocab",
];

function showPanel(id) {
  closeWordPopover();
  for (const name of PANELS) {
    const el = document.getElementById(`panel-${name}`);
    if (el) el.classList.toggle("hidden", id !== name);
  }
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

function syncPreferencePanels() {
  const style = document.querySelector('input[name="style"]:checked').value;
  const type = document.getElementById("ex-type").value;
  const box = document.getElementById("preferences-box");
  const standard = document.getElementById("preferences-standard");
  const drillsOnly = document.getElementById("preferences-drills-only");
  const drillsHintWeak = document.getElementById("drills-hint-weak");
  const drillsHintPrefs = document.getElementById("drills-hint-prefs");
  const drillGrid = document.getElementById("drill-pref-grid-wrap");

  const showPrefsShell =
    style === "preferences" || (style === "weaknesses" && type === "drills");
  box.classList.toggle("hidden", !showPrefsShell);
  if (!showPrefsShell) return;

  const isDrills = type === "drills";
  const showStandard = style === "preferences" && !isDrills;
  standard.classList.toggle("hidden", !showStandard);
  drillsOnly.classList.toggle("hidden", !isDrills);

  // Drills:
  // - weaknesses: choose axis only
  // - preferences: choose axis + subtopics
  if (isDrills) {
    const wantsSubtopics = style === "preferences";
    if (drillsHintWeak) drillsHintWeak.classList.toggle("hidden", wantsSubtopics);
    if (drillsHintPrefs) drillsHintPrefs.classList.toggle("hidden", !wantsSubtopics);
    if (drillGrid) drillGrid.classList.toggle("hidden", !wantsSubtopics);
    if (wantsSubtopics) rebuildDrillPrefGrid();
  }
}

function onStyleChange() {
  syncPreferencePanels();
}

async function onLogin(ev) {
  ev.preventDefault();
  setStatus("");
  const username = document.getElementById("login-username").value.trim();
  const key = document.getElementById("login-key").value.trim();
  const newUser = document.getElementById("login-new").checked;
  if (!username) {
    setStatus("Please enter a username.", true);
    return;
  }
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    const res = await withBusy(submitBtn, "Signing in…", () =>
      api("POST", "/user/login", { username, key, new: newUser }),
    );
    setUsername(username);
    updateExerciseUserLabel();
    await routeToStep(res.step);
  } catch (e) {
    setStatus(e.message, true);
  }
}

/**
 * Sends the learner to whichever onboarding stage they still owe us.
 * @param {"goals" | "placement" | "ready"} step
 */
async function routeToStep(step) {
  if (step === "goals") {
    setWalkthroughAllowed(false);
    setStatus("Welcome — a few quick questions first.", false);
    showPanel("goals");
    return;
  }
  if (step === "placement") {
    setWalkthroughAllowed(false);
    setStatus("");
    showPanel("placement");
    await loadPlacementForm();
    return;
  }
  setWalkthroughAllowed(true);
  setStatus("Today’s practice is ready.", false);
  showPanel("exercise");
  await refreshLevelSummary();
  await loadRecommendations();
  maybeOfferWalkthrough();
}

async function refreshLevelSummary() {
  const u = getUsername();
  const el = document.getElementById("level-summary");
  if (!u || !el) return;
  try {
    const res = await api("GET", `/onboarding/status?username=${encodeURIComponent(u)}`);
    state.plan = res.plan;
    renderLevelSummary(res.plan);
    const length = res.goals?.length_preference;
    const sel = document.getElementById("ex-length");
    if (length && sel) sel.value = length;
  } catch {
    el.hidden = true;
  }
}

async function loadRecommendations() {
  const root = document.getElementById("daily-root");
  const u = getUsername();
  if (!root || !u) return;
  root.innerHTML = '<p class="hint">Setting up today…</p>';
  try {
    const res = await api("POST", "/exercise/recommend", { username: u, day: localDate() });
    state.recommendations = res;
    renderHomePlan(res);
  } catch (e) {
    root.innerHTML = "";
    const p = document.createElement("p");
    p.className = "hint";
    p.textContent = "We couldn't load today. Open Extra practice to pick an exercise yourself.";
    root.appendChild(p);
  }
}

function localDate() {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

function renderHomePlan(plan) {
  const root = document.getElementById("daily-root");
  const extrasRoot = document.getElementById("extras-root");
  const lead = document.getElementById("daily-lead");
  if (!root) return;
  root.innerHTML = "";
  if (lead) {
    if (plan?.complete) {
      lead.textContent =
        "Today’s writing, reading, listening, and speaking are done. Keep learning below whenever you like.";
    } else if (plan?.remaining === 4) {
      lead.textContent =
        "One writing, reading, listening, and speaking session today. Learning stays open underneath.";
    } else {
      const left = Number(plan?.remaining) || 0;
      lead.textContent = `${left} left today. Learning stays open underneath.`;
    }
  }
  const slots = plan?.daily || [];
  if (!slots.length) {
    const p = document.createElement("p");
    p.className = "hint";
    p.textContent = "Open Extra practice to pick an exercise.";
    root.appendChild(p);
  } else {
    slots.forEach((slot) => root.appendChild(dailySlotCard(slot)));
  }
  if (extrasRoot) {
    extrasRoot.innerHTML = "";
    (plan?.extras || []).forEach((card) => extrasRoot.appendChild(recommendCard(card)));
  }
}

function dailySlotCard(slot) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "recommend-card daily-card";
  btn.setAttribute("data-kind", slot.done ? "done" : "daily");
  if (slot.done) {
    btn.disabled = true;
    btn.setAttribute("aria-disabled", "true");
  }

  const eyebrow = document.createElement("span");
  eyebrow.className = "recommend-card-kind";
  eyebrow.textContent = slot.kind_label || (slot.done ? "Done" : "Today");

  const title = document.createElement("span");
  title.className = "recommend-card-title";
  title.textContent = slot.title_en || slot.type || "";

  const reason = document.createElement("span");
  reason.className = "recommend-card-reason";
  reason.textContent = slot.reason_en || "";

  btn.appendChild(eyebrow);
  btn.appendChild(title);
  btn.appendChild(reason);
  const minutes = Number(slot.estimated_minutes) || 0;
  if (minutes && !slot.done) {
    const meta = document.createElement("span");
    meta.className = "recommend-card-meta";
    meta.textContent = `About ${minutes} min`;
    btn.appendChild(meta);
  }
  if (!slot.done) {
    btn.addEventListener("click", () => startFromCard(slot, btn));
  }
  return btn;
}

function recommendCard(card) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "recommend-card";
  btn.setAttribute("data-kind", card.kind || "");

  const eyebrow = document.createElement("span");
  eyebrow.className = "recommend-card-kind";
  eyebrow.textContent = card.kind_label || card.kind || "";

  const title = document.createElement("span");
  title.className = "recommend-card-title";
  title.textContent = card.title_en || "";

  const reason = document.createElement("span");
  reason.className = "recommend-card-reason";
  reason.textContent = card.reason_en || "";

  const meta = document.createElement("span");
  meta.className = "recommend-card-meta";
  const minutes = Number(card.estimated_minutes) || 0;
  meta.textContent = minutes ? `About ${minutes} min` : "";

  btn.appendChild(eyebrow);
  btn.appendChild(title);
  btn.appendChild(reason);
  if (minutes) btn.appendChild(meta);
  btn.addEventListener("click", () => startFromCard(card, btn));
  return btn;
}

async function startFromCard(card, btn) {
  setStatus("");
  if ((card.kind || "") === "vocab") {
    await startVocabReview(btn);
    return;
  }
  const body = {
    username: getUsername(),
    type: card.type,
    style: card.style || "preferences",
    preferences: card.focus || null,
    length: currentLength(),
  };
  await startExercise(body, btn);
}

function currentLength() {
  return document.getElementById("ex-length")?.value || "standard";
}

async function startExercise(body, btn) {
  try {
    await withBusy(btn || null, "Starting…", () =>
      api("POST", "/exercise/generate", body).then((res) => {
        state.exercise = res.exercise;
        state.writingPrompt = null;
        state.readingPrompt = null;
        state.drills = null;
        state.listeningPrompt = null;
        state.speakingPrompt = null;
        state.vocabReview = null;
        updateFocusWidgetFromExercise(state.exercise);
        showPanel("practice");
        return runGenerateForCurrentExercise();
      }),
    );
    setStatus("Ready — your exercise is below.", false);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function renderLevelSummary(plan) {
  const el = document.getElementById("level-summary");
  if (!el) return;
  syncProgressUnlock(plan?.completed_exercises);
  const level = plan?.current_level ?? displayLevel(plan?.current_band);
  if (!plan || (level === "" && !plan.current_gloss)) {
    el.hidden = true;
    return;
  }
  el.innerHTML = "";

  const now = document.createElement("p");
  now.className = "level-summary-now";
  now.textContent = `Your level: ${levelWithGloss(level, plan.current_gloss)}`;
  el.appendChild(now);

  const goalLevel = plan.target_level ?? displayLevel(plan.target_band);
  if (plan.target_band || goalLevel !== "") {
    const next = document.createElement("p");
    next.className = "level-summary-goal";
    const duration = humanizeDuration(plan.estimated_weeks);
    if (plan.half_steps_remaining === 0) {
      next.textContent = `You've reached your goal of ${goalLevel}. Keep practising to hold it.`;
    } else if (duration) {
      next.textContent = `Goal: ${levelWithGloss(goalLevel, plan.target_gloss)}. At your current pace that's ${duration} of steady practice.`;
    } else {
      next.textContent = `Goal: ${levelWithGloss(goalLevel, plan.target_gloss)}.`;
    }
    el.appendChild(next);
  }

  el.hidden = false;
}

async function onGoalsSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  const username = getUsername();
  if (!username) {
    showPanel("login");
    return;
  }
  const goals = {
    direction: document.getElementById("goal-direction").value,
    desired_band: document.getElementById("goal-target").value,
    weekly_time: document.getElementById("goal-time").value,
    length_preference: document.getElementById("goal-length").value,
  };
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    const res = await withBusy(submitBtn, "Saving…", () =>
      api("POST", "/onboarding/goals", { username, goals }),
    );
    await routeToStep(res.step);
  } catch (e) {
    setStatus(e.message, true);
  }
}

async function loadPlacementForm() {
  const root = document.getElementById("placement-root");
  if (!root) return;
  root.innerHTML = '<p class="hint">Loading…</p>';
  try {
    const res = await api("GET", "/onboarding/placement");
    state.placementForm = res.form;
    renderPlacementForm(res.form);
  } catch (e) {
    root.innerHTML = "";
    setStatus(e.message, true);
  }
}

function renderPlacementForm(form) {
  const root = document.getElementById("placement-root");
  root.innerHTML = "";

  const mcqSection = document.createElement("div");
  mcqSection.className = "placement-section";
  const mcqTitle = document.createElement("p");
  mcqTitle.className = "help-section-title";
  mcqTitle.textContent = "Part 1 — Choose the best option";
  mcqSection.appendChild(mcqTitle);

  (form.mcq || []).forEach((item, idx) => {
    const block = document.createElement("fieldset");
    block.className = "fieldset-plain placement-question";
    const legend = document.createElement("legend");
    legend.className = "fake-label";
    legend.textContent = `${idx + 1}. ${item.prompt}`;
    block.appendChild(legend);

    const row = document.createElement("div");
    row.className = "row row-tight";
    item.options.forEach((option) => {
      const label = document.createElement("label");
      label.className = "choice-inline";
      const input = document.createElement("input");
      input.type = "radio";
      input.name = `mcq-${item.id}`;
      input.value = option;
      label.appendChild(input);
      label.appendChild(document.createTextNode(` ${option}`));
      row.appendChild(label);
    });
    block.appendChild(row);
    mcqSection.appendChild(block);
  });
  root.appendChild(mcqSection);

  const writingSection = document.createElement("div");
  writingSection.className = "placement-section";
  const writingTitle = document.createElement("p");
  writingTitle.className = "help-section-title";
  writingTitle.textContent = "Part 2 — Write a little Spanish";
  const writingPrompt = document.createElement("p");
  writingPrompt.className = "hint";
  writingPrompt.textContent = `${form.writing_prompt_en} Aim for about ${form.writing_target_words} words, but write as much or as little as you can.`;
  const writingInput = document.createElement("textarea");
  writingInput.id = "placement-writing";
  writingInput.rows = 6;
  writingInput.placeholder = "Write in Spanish here, or leave blank if you're a complete beginner.";
  writingSection.appendChild(writingTitle);
  writingSection.appendChild(writingPrompt);
  writingSection.appendChild(writingInput);
  root.appendChild(writingSection);

  const readingSection = document.createElement("div");
  readingSection.className = "placement-section";
  const readingTitle = document.createElement("p");
  readingTitle.className = "help-section-title";
  readingTitle.textContent = "Part 3 — Read and answer";
  const passage = renderClickableSpanish(form.reading_passage);
  readingSection.appendChild(readingTitle);
  readingSection.appendChild(translateHint());
  readingSection.appendChild(passage);

  (form.reading_questions || []).forEach((question, idx) => {
    const label = document.createElement("label");
    label.htmlFor = `placement-reading-${idx}`;
    label.textContent = question;
    const input = document.createElement("input");
    input.type = "text";
    input.id = `placement-reading-${idx}`;
    input.className = "placement-reading-answer";
    input.placeholder = "Answer in Spanish or English";
    readingSection.appendChild(label);
    readingSection.appendChild(input);
  });
  root.appendChild(readingSection);
}

async function onPlacementSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  const username = getUsername();
  const form = state.placementForm;
  if (!username || !form) {
    showPanel("login");
    return;
  }

  const mcqAnswers = {};
  (form.mcq || []).forEach((item) => {
    const picked = document.querySelector(`input[name="mcq-${item.id}"]:checked`);
    if (picked) mcqAnswers[item.id] = picked.value;
  });

  const readingAnswers = (form.reading_questions || []).map(
    (_, idx) => document.getElementById(`placement-reading-${idx}`)?.value || "",
  );

  const submission = {
    mcq_answers: mcqAnswers,
    writing_response: document.getElementById("placement-writing")?.value || "",
    reading_answers: readingAnswers,
  };

  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    const res = await withBusy(submitBtn, "Working out your level…", () =>
      api("POST", "/onboarding/placement", { username, submission }),
    );
    state.plan = res.plan;
    const level = res.assigned_level ?? displayLevel(res.assigned_band);
    await routeToStep("ready");
    setStatus(
      `You're starting at ${levelWithGloss(level, res.gloss)}. ${res.notes_en}`,
      false,
    );
  } catch (e) {
    setStatus(e.message, true);
  }
}

function readExerciseFormBody() {
  const username = getUsername();
  const type = document.getElementById("ex-type").value;
  const style = document.querySelector('input[name="style"]:checked').value;
  let preferences = null;

  if (type === "drills") {
    const axis =
      document.querySelector('input[name="drill-pref-axis"]:checked')?.value ||
      "tenses";
    if (style === "preferences") {
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
      // Weak areas: axis only (no subtopics).
      preferences =
        axis === "grammar"
          ? {
              focus_tenses: null,
              focus_grammar: ["grammar"],
              focus_topics: null,
            }
          : {
              focus_tenses: ["tenses"],
              focus_grammar: null,
              focus_topics: null,
            };
    }
  } else if (style === "preferences") {
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

  return { username, type, style, preferences, length: currentLength() };
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
  await startExercise(body, submitBtn);
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
  try {
    if (ex.exercise_type === "writing") {
      const res = await api("POST", "/writing/generate", { username: u });
      state.writingPrompt = res.prompt;
      renderWritingPractice();
    } else if (ex.exercise_type === "reading") {
      const res = await api("POST", "/reading/generate", { username: u });
      state.readingPrompt = res.prompt;
      renderReadingPractice();
    } else if (ex.exercise_type === "listening") {
      const res = await api("POST", "/listening/generate", { username: u });
      state.listeningPrompt = res;
      renderListeningPractice();
    } else if (ex.exercise_type === "speaking") {
      const res = await api("POST", "/speaking/generate", { username: u });
      state.speakingPrompt = res.prompt;
      renderSpeakingPractice();
    } else if (ex.exercise_type === "drills") {
      const res = await api("POST", "/drills/generate", { username: u });
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
  root.appendChild(focusChipRow());
  root.appendChild(translateHint());
  root.appendChild(renderClickableSpanish(prompt));
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
    announceSubmission(res, "Feedback is ready below.");
    showResultsWriting(res, text);
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

function showResultsWriting(res, userResponse) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const fb = document.createElement("div");
  fb.className = "feedback-block";
  const hSum = document.createElement("h3");
  hSum.textContent = "Summary";
  fb.appendChild(hSum);
  // API shape (current): { feedback: WritingSummary, corrections: TextCorrection }
  // Older UI experiments used: { summarised_correction, detailed_correction }
  const sum = res?.feedback ?? res?.summarised_correction ?? null;
  fb.appendChild(
    elBlock(
      [
        sum?.general_feedback ?? "",
        "",
        sum?.tense_edits ?? "",
        "",
        sum?.grammar_edits ?? "",
        "",
        sum?.topic_edits ?? "",
      ].join("\n"),
    ),
  );

  const hUser = document.createElement("h3");
  hUser.textContent = "Your response";
  fb.appendChild(hUser);
  fb.appendChild(elBlock(userResponse ?? ""));

  const dc = res?.corrections ?? res?.detailed_correction ?? null;
  const hCorr = document.createElement("h3");
  hCorr.textContent = "Corrected version";
  fb.appendChild(hCorr);
  fb.appendChild(elBlock(dc?.corrected_version || ""));

  const hDetail = document.createElement("h3");
  hDetail.textContent = "Corrections in detail";
  fb.appendChild(hDetail);
  const detailWrap = document.createElement("div");
  appendEditSection(detailWrap, "Verb tenses", dc?.tense_errors);
  appendEditSection(detailWrap, "Grammar", dc?.grammar_errors);
  appendEditSection(detailWrap, "Topic / vocabulary", dc?.topic_errors);
  appendEditSection(detailWrap, "Typos & small fixes", dc?.typos);
  appendEditSection(detailWrap, "Other", dc?.other_mistakes);
  if (!detailWrap.children.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No structured edits were returned — see the summary above.";
    detailWrap.appendChild(empty);
  }
  fb.appendChild(detailWrap);
  appendRelatedLessons(fb, res?.lessons);
  root.appendChild(fb);
}

function elBlock(text) {
  const p = document.createElement("p");
  p.className = "passage";
  p.textContent = text;
  return p;
}

let focusDrawerOpen = false;

function ensureFocusWidget() {
  if (document.getElementById("focus-tab")) return;
  const tab = document.createElement("div");
  tab.id = "focus-tab";
  tab.className = "focus-tab hidden";

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "focus-tab-btn";
  btn.textContent = "Focus";
  btn.addEventListener("click", () => {
    focusDrawerOpen = !focusDrawerOpen;
    const drawer = document.getElementById("focus-drawer");
    if (drawer) drawer.classList.toggle("hidden", !focusDrawerOpen);
  });
  tab.appendChild(btn);

  const drawer = document.createElement("aside");
  drawer.id = "focus-drawer";
  drawer.className = "focus-drawer hidden";
  drawer.setAttribute("aria-label", "Exercise focus");

  document.body.appendChild(tab);
  document.body.appendChild(drawer);
}

function setFocusWidgetVisible(isVisible) {
  ensureFocusWidget();
  const tab = document.getElementById("focus-tab");
  const drawer = document.getElementById("focus-drawer");
  if (tab) tab.classList.toggle("hidden", !isVisible);
  if (!isVisible) {
    focusDrawerOpen = false;
    if (drawer) drawer.classList.add("hidden");
  }
}

function updateFocusWidgetFromExercise(ex) {
  ensureFocusWidget();
  const drawer = document.getElementById("focus-drawer");
  if (!drawer) return;
  if (!ex) {
    drawer.innerHTML = "";
    setFocusWidgetVisible(false);
    return;
  }

  const aof = ex.areas_of_focus || {};
  const band = ex.band || ex.exercise_config?.band || "";
  const type = ex.exercise_type || "";

  const normList = (arr) =>
    (Array.isArray(arr) ? arr : [])
      .filter((x) => x != null && String(x).trim() !== "")
      .map((x) => String(x));

  const tenses = normList(aof.focus_tenses);
  const grammar = normList(aof.focus_grammar);
  const topics = normList(aof.focus_topics);

  const section = (title, items) => {
    const wrap = document.createElement("div");
    wrap.className = "focus-group";
    const h = document.createElement("p");
    h.className = "focus-group-title";
    h.textContent = title;
    wrap.appendChild(h);
    if (!items.length) {
      const p = document.createElement("p");
      p.className = "focus-meta";
      p.style.margin = "0";
      p.textContent = "—";
      wrap.appendChild(p);
      return wrap;
    }
    const ul = document.createElement("ul");
    items.forEach((it) => {
      const li = document.createElement("li");
      li.textContent = humanizeKey(it);
      ul.appendChild(li);
    });
    wrap.appendChild(ul);
    return wrap;
  };

  drawer.innerHTML = "";
  const h3 = document.createElement("h3");
  h3.textContent = "Focus";
  const meta = document.createElement("p");
  meta.className = "focus-meta";
  meta.textContent = band
    ? `Type: ${humanizeKey(type)} • Level: ${levelWithGloss(displayLevel(band), bandLabel(band))}`
    : `Type: ${humanizeKey(type)}`;
  drawer.appendChild(h3);
  drawer.appendChild(meta);
  drawer.appendChild(section("Tenses", tenses));
  drawer.appendChild(section("Grammar", grammar));
  drawer.appendChild(section("Topics", topics));

  setFocusWidgetVisible(true);
}

function renderReadingPractice() {
  const root = document.getElementById("practice-root");
  const pr = state.readingPrompt;
  root.innerHTML = "";
  root.appendChild(focusChipRow());
  root.appendChild(translateHint());
  root.appendChild(renderClickableSpanish(pr.passage));
  const form = document.createElement("form");
  form.id = "form-reading";
  pr.questions.forEach((q, i) => {
    const wrap = document.createElement("div");
    wrap.className = "question-block";
    const lab = document.createElement("label");
    lab.htmlFor = `reading-q-${i}`;
    const prefix = document.createElement("span");
    prefix.textContent = `Question ${i + 1}: `;
    lab.appendChild(prefix);
    lab.appendChild(renderClickableSpanish(q, "", "span"));
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
    announceSubmission(res, "Feedback is ready below.");
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

  const feedback = res.feedback ?? res.correction;
  const perQuestion = feedback?.individual_questions ?? [];
  const textList = res.corrections?.corrections ?? [];

  const hTitle = document.createElement("h3");
  hTitle.textContent = "Reading — your results";
  fb.appendChild(hTitle);

  const hOverall = document.createElement("h3");
  hOverall.textContent = "Overall";
  fb.appendChild(hOverall);
  fb.appendChild(elBlock(feedback?.general_feedback ?? ""));

  const n = Math.max(
    questions.length,
    perQuestion.length,
    textList.length,
  );

  for (let i = 0; i < n; i++) {
    const card = document.createElement("div");
    card.className = "reading-q-card";

    const hq = document.createElement("h4");
    hq.textContent = `Question ${i + 1}`;
    card.appendChild(hq);

    const promptLine = document.createElement("p");
    promptLine.className = "reading-meta";
    promptLine.innerHTML = `<strong>Prompt:</strong> ${escapeHtml(questions[i] ?? "")}`;
    card.appendChild(promptLine);

    const yourAnsLabel = document.createElement("p");
    yourAnsLabel.className = "reading-section-label";
    yourAnsLabel.textContent = "Your answer";
    card.appendChild(yourAnsLabel);
    card.appendChild(elBlock(userResponses[i] ?? ""));

    const compLabel = document.createElement("p");
    compLabel.className = "reading-section-label";
    compLabel.textContent = "Comprehension feedback";
    card.appendChild(compLabel);
    card.appendChild(elBlock(perQuestion[i] ?? ""));

    const tc = textList[i];
    if (tc && typeof tc === "object") {
      const sugLabel = document.createElement("p");
      sugLabel.className = "reading-section-label";
      sugLabel.textContent = "Suggested wording";
      card.appendChild(sugLabel);
      card.appendChild(elBlock(tc.corrected_version ?? ""));

      const detailWrap = document.createElement("div");
      appendEditSection(detailWrap, "Verb tenses", tc.tense_errors);
      appendEditSection(detailWrap, "Grammar", tc.grammar_errors);
      appendEditSection(detailWrap, "Topic / vocabulary", tc.topic_errors);
      appendEditSection(detailWrap, "Typos & small fixes", tc.typos);
      appendEditSection(detailWrap, "Other", tc.other_mistakes);
      if (detailWrap.children.length) {
        const detLabel = document.createElement("p");
        detLabel.className = "reading-section-label";
        detLabel.textContent = "Text corrections";
        card.appendChild(detLabel);
        card.appendChild(detailWrap);
      }
    }

    fb.appendChild(card);
  }

  appendRelatedLessons(fb, res?.lessons);
  root.appendChild(fb);
}

function renderDrillsPractice() {
  const root = document.getElementById("practice-root");
  const drills = state.drills;
  root.innerHTML = "";
  root.appendChild(focusChipRow());
  const typesPresent = orderedDrillKeysWithDrills(drills.drill_sets);
  if (typesPresent.length === 0) {
    root.textContent = "No drills loaded.";
    return;
  }

  const form = document.createElement("form");
  form.id = "form-drills";
  form.className = "form-drills-wizard";

  const progressRow = document.createElement("div");
  progressRow.className = "drill-progress-row";
  progressRow.setAttribute("aria-live", "polite");
  const countEl = document.createElement("span");
  countEl.className = "drill-progress-count";
  countEl.id = "drill-progress-count";
  const descEl = document.createElement("p");
  descEl.className = "drill-progress-label";
  descEl.id = "drill-progress-desc";
  progressRow.appendChild(countEl);
  progressRow.appendChild(descEl);

  const bar = document.createElement("div");
  bar.className = "drill-progress-bar";
  bar.setAttribute("role", "progressbar");
  bar.setAttribute("aria-valuemin", "1");
  bar.setAttribute("aria-valuemax", String(typesPresent.length));
  bar.setAttribute("aria-labelledby", "drill-progress-desc");
  const fill = document.createElement("div");
  fill.className = "drill-progress-fill";
  fill.id = "drill-progress-fill";
  bar.appendChild(fill);

  const pagesWrap = document.createElement("div");
  pagesWrap.className = "drill-wizard-pages";

  for (let si = 0; si < typesPresent.length; si++) {
    const dt = typesPresent[si];
    const set = drills.drill_sets[dt];
    const section = document.createElement("section");
    section.className = "drill-type-section drill-wizard-page";
    if (si === 0) section.classList.add("is-active");
    section.setAttribute("aria-labelledby", `drill-type-head-${dt}`);
    section.setAttribute("aria-hidden", si === 0 ? "false" : "true");
    const h = document.createElement("h3");
    h.className = "drill-type-title";
    h.id = `drill-type-head-${dt}`;
    h.textContent = humanizeKeyTitle(dt);
    section.appendChild(h);
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
        const opts = shuffleArray(d.options);
        opts.forEach((opt) => {
          const li = document.createElement("li");
          const lab = document.createElement("label");
          const radio = document.createElement("input");
          radio.type = "radio";
          radio.name = name;
          radio.value = opt;
          radio.required = true;
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
      section.appendChild(block);
    });
    pagesWrap.appendChild(section);
  }

  const nav = document.createElement("div");
  nav.className = "drill-wizard-nav";
  const btnBack = document.createElement("button");
  btnBack.type = "button";
  btnBack.className = "btn btn-secondary";
  btnBack.textContent = "Back";
  const btnNext = document.createElement("button");
  btnNext.type = "button";
  btnNext.className = "btn btn-primary";
  btnNext.textContent = "Next";
  const submitBtn = document.createElement("button");
  submitBtn.type = "submit";
  submitBtn.className = "btn btn-primary";
  submitBtn.innerHTML = '<span class="btn-label">Submit drills</span>';

  nav.appendChild(btnBack);
  nav.appendChild(btnNext);
  nav.appendChild(submitBtn);

  form.appendChild(progressRow);
  form.appendChild(bar);
  form.appendChild(pagesWrap);
  form.appendChild(nav);

  let step = 0;
  const n = typesPresent.length;

  function syncWizard() {
    countEl.textContent = `${step + 1}/${n}`;
    const dt = typesPresent[step];
    const title = humanizeKeyTitle(dt);
    const blurb = DRILL_STEP_BLURB[dt] || "";
    descEl.innerHTML = `<strong>${escapeHtml(title)}</strong> — ${escapeHtml(blurb)}`;
    fill.style.width = `${((step + 1) / n) * 100}%`;
    bar.setAttribute("aria-valuenow", String(step + 1));

    const pages = pagesWrap.querySelectorAll(".drill-wizard-page");
    pages.forEach((el, j) => {
      const on = j === step;
      el.classList.toggle("is-active", on);
      el.setAttribute("aria-hidden", on ? "false" : "true");
    });

    btnBack.disabled = step === 0;
    const last = step === n - 1;
    btnNext.hidden = last;
    submitBtn.hidden = !last;
  }

  btnBack.addEventListener("click", () => {
    if (step > 0) {
      step -= 1;
      syncWizard();
    }
  });

  btnNext.addEventListener("click", () => {
    if (step < n - 1) {
      step += 1;
      syncWizard();
    }
  });

  form.addEventListener("submit", onDrillsSubmit);
  root.appendChild(form);
  syncWizard();
}

function collectDrillResponses() {
  const drills = state.drills;
  /** @type {Record<string, string[]>} */
  const responses = {};
  for (const dt of orderedDrillKeysWithDrills(drills.drill_sets)) {
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
    announceSubmission(res, "Results are ready below.");
    showResultsDrills(res);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function showResultsDrills(res) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const fb = document.createElement("div");
  fb.className = "feedback-block drill-results-feedback";
  const md = res.marked_drills;

  const hTitle = document.createElement("h3");
  hTitle.textContent = "Drills — your results";
  fb.appendChild(hTitle);

  if (md.stats) {
    const hOverall = document.createElement("h3");
    hOverall.textContent = "Overall";
    fb.appendChild(hOverall);
    fb.appendChild(
      elBlock(
        `${md.stats.correct_attempts} / ${md.stats.total_attempts} correct`,
      ),
    );
  }

  /** @type {Record<string, object>} */
  const setsByType = {};
  for (const set of md.marked_drill_sets || []) {
    const k = set.drill_type;
    if (k != null) setsByType[k] = set;
  }

  const grid = document.createElement("div");
  grid.className = "drill-feedback-grid";
  grid.setAttribute("aria-label", "Drill feedback by type");

  for (const dt of orderedDrillKeysWithMarked(setsByType)) {
    const set = setsByType[dt];
    if (!set || !set.marked_drills?.length) continue;

    const section = document.createElement("section");
    section.className = "drill-type-section drill-feedback-tile";
    section.setAttribute("aria-labelledby", `drill-feedback-head-${dt}`);
    const typeH = document.createElement("h3");
    typeH.className = "drill-type-title";
    typeH.id = `drill-feedback-head-${dt}`;
    typeH.textContent = humanizeKeyTitle(dt);
    section.appendChild(typeH);

    let qIdx = 0;
    for (const row of set.marked_drills) {
      qIdx += 1;
      const card = document.createElement("div");
      card.className = "reading-q-card";

      const head = document.createElement("div");
      head.className = "drill-card-head";
      const hq = document.createElement("h4");
      hq.textContent = `Question ${qIdx}`;
      const badge = document.createElement("span");
      badge.className = row.is_correct ? "badge badge-ok" : "badge badge-no";
      badge.textContent = row.is_correct ? "Correct" : "Review";
      head.appendChild(hq);
      head.appendChild(badge);
      card.appendChild(head);

      const promptLine = document.createElement("p");
      promptLine.className = "reading-meta";
      promptLine.innerHTML = `<strong>Prompt:</strong> ${escapeHtml(row.prompt || "")}`;
      card.appendChild(promptLine);

      const yourAnsLabel = document.createElement("p");
      yourAnsLabel.className = "reading-section-label";
      yourAnsLabel.textContent = "Your answer";
      card.appendChild(yourAnsLabel);
      card.appendChild(elBlock(row.user_response ?? ""));

      const correctLabel = document.createElement("p");
      correctLabel.className = "reading-section-label";
      correctLabel.textContent = "Correct answer";
      card.appendChild(correctLabel);
      card.appendChild(elBlock(row.answer ?? ""));

      const commentStr =
        row.comment != null && String(row.comment).trim()
          ? String(row.comment).trim()
          : null;
      if (commentStr) {
        const commLabel = document.createElement("p");
        commLabel.className = "reading-section-label";
        commLabel.textContent = "Comment";
        card.appendChild(commLabel);
        card.appendChild(elBlock(commentStr));
      }

      section.appendChild(card);
    }
    grid.appendChild(section);
  }

  if (grid.children.length) {
    fb.appendChild(grid);
  }

  appendRelatedLessons(fb, res?.lessons);
  root.appendChild(fb);
}

function appendRelatedLessons(parent, lessons) {
  if (!lessons || !lessons.length) return;
  const wrap = document.createElement("div");
  wrap.className = "related-lessons";
  const h = document.createElement("h3");
  h.textContent = "Related notes";
  wrap.appendChild(h);
  const hint = document.createElement("p");
  hint.className = "hint";
  hint.textContent = "These match what you just practised. Open one if you want a short explanation.";
  wrap.appendChild(hint);
  const row = document.createElement("div");
  row.className = "lesson-chip-row";
  const detail = document.createElement("div");
  detail.className = "lesson-inline";
  lessons.forEach((card) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "lesson-chip";
    btn.textContent = card.title_en || card.key;
    btn.addEventListener("click", async () => {
      try {
        const res = await api("GET", `/learn/lesson/${encodeURIComponent(card.key)}`);
        detail.innerHTML = "";
        detail.appendChild(renderLesson(res.lesson));
        detail.hidden = false;
      } catch (e) {
        setStatus(e.message, true);
      }
    });
    row.appendChild(btn);
  });
  wrap.appendChild(row);
  detail.hidden = true;
  wrap.appendChild(detail);
  parent.appendChild(wrap);
}

function renderLesson(lesson) {
  const article = document.createElement("article");
  article.className = "lesson-article";

  const title = document.createElement("h3");
  title.className = "lesson-title";
  title.textContent = lesson.title_en || lesson.key;
  article.appendChild(title);

  if (lesson.rule) {
    article.appendChild(elBlock(lesson.rule));
  }

  if (lesson.when_to_use?.length) {
    const ul = document.createElement("ul");
    ul.className = "lesson-uses";
    lesson.when_to_use.forEach((line) => {
      const li = document.createElement("li");
      li.textContent = line;
      ul.appendChild(li);
    });
    article.appendChild(ul);
  }

  if (lesson.table && Object.keys(lesson.table).length) {
    article.appendChild(renderConjugationTable(lesson.table));
  }

  (lesson.examples || []).forEach((ex) => {
    const card = document.createElement("div");
    card.className = "lesson-example";
    const es = renderClickableSpanish(ex.es || "", "lesson-example-es");
    card.appendChild(es);
    const en = document.createElement("p");
    en.className = "lesson-example-en";
    en.textContent = ex.en || "";
    card.appendChild(en);
    if (ex.note) {
      const note = document.createElement("p");
      note.className = "hint";
      note.textContent = ex.note;
      card.appendChild(note);
    }
    article.appendChild(card);
  });

  if (lesson.common_mistake) {
    const warn = document.createElement("p");
    warn.className = "lesson-mistake";
    warn.textContent = `Watch out: ${lesson.common_mistake}`;
    article.appendChild(warn);
  }

  return article;
}

function renderConjugationTable(table) {
  const verbs = Object.keys(table);
  const personSet = new Set();
  verbs.forEach((verb) => {
    Object.keys(table[verb] || {}).forEach((p) => personSet.add(p));
  });
  const persons = [
    ...PERSON_ORDER.filter((p) => personSet.has(p)),
    ...[...personSet].filter((p) => !PERSON_ORDER.includes(p)),
  ];

  const wrap = document.createElement("div");
  wrap.className = "conj-table-wrap";
  const tbl = document.createElement("table");
  tbl.className = "conj-table";
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  headRow.appendChild(document.createElement("th"));
  verbs.forEach((verb) => {
    const th = document.createElement("th");
    th.textContent = verb;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  tbl.appendChild(thead);

  const tbody = document.createElement("tbody");
  persons.forEach((person) => {
    const tr = document.createElement("tr");
    const th = document.createElement("th");
    th.scope = "row";
    th.textContent = person;
    tr.appendChild(th);
    verbs.forEach((verb) => {
      const td = document.createElement("td");
      td.textContent = table[verb]?.[person] || "";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  tbl.appendChild(tbody);
  wrap.appendChild(tbl);
  return wrap;
}

function goHome() {
  showPanel("exercise");
  refreshLevelSummary();
  loadRecommendations();
}

async function onLearnClick() {
  setStatus("");
  const btn = document.getElementById("btn-learn");
  try {
    const res = await withBusy(btn, "Loading…", () => api("GET", "/learn/index"));
    renderLearnIndex(res.lessons || []);
    showPanel("learn");
  } catch (e) {
    setStatus(e.message, true);
  }
}

function renderLearnIndex(lessons) {
  const root = document.getElementById("learn-root");
  root.innerHTML = "";
  const groups = [
    { axis: "tense", title: "Tenses" },
    { axis: "grammar", title: "Grammar" },
  ];
  groups.forEach((group) => {
    const items = lessons.filter((l) => l.axis === group.axis);
    if (!items.length) return;
    const h = document.createElement("h3");
    h.textContent = group.title;
    root.appendChild(h);
    const list = document.createElement("div");
    list.className = "learn-index";
    items.forEach((card) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "learn-index-card";
      const title = document.createElement("span");
      title.className = "learn-index-title";
      title.textContent = card.title_en;
      const summary = document.createElement("span");
      summary.className = "hint";
      summary.textContent = card.summary || "";
      btn.appendChild(title);
      btn.appendChild(summary);
      btn.addEventListener("click", () => openLearnLesson(card.key));
      list.appendChild(btn);
    });
    root.appendChild(list);
  });
}

async function openLearnLesson(key) {
  setStatus("");
  try {
    const res = await api("GET", `/learn/lesson/${encodeURIComponent(key)}`);
    const root = document.getElementById("learn-root");
    root.innerHTML = "";
    const back = document.createElement("button");
    back.type = "button";
    back.className = "btn btn-ghost lesson-back";
    back.innerHTML = '<span class="btn-label">All notes</span>';
    back.addEventListener("click", onLearnClick);
    root.appendChild(back);
    root.appendChild(renderLesson(res.lesson));
    showPanel("learn");
  } catch (e) {
    setStatus(e.message, true);
  }
}

function renderChatHistory(history) {
  const root = document.getElementById("chat-root");
  root.innerHTML = "";
  if (!history || !history.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No questions yet. Ask about a tense, a grammar point, or a mistake from a recent exercise.";
    root.appendChild(empty);
    return;
  }
  history.forEach((turn) => {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble chat-bubble-${turn.role === "assistant" ? "assistant" : "user"}`;
    bubble.textContent = turn.text || "";
    root.appendChild(bubble);
    if (turn.role === "assistant" && turn.lesson_keys?.length) {
      const row = document.createElement("div");
      row.className = "lesson-chip-row";
      turn.lesson_keys.forEach((key) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "lesson-chip";
        btn.textContent = humanizeKeyTitle(key);
        btn.addEventListener("click", () => openLearnLesson(key));
        row.appendChild(btn);
      });
      root.appendChild(row);
    }
  });
  root.scrollTop = root.scrollHeight;
}

async function onChatClick() {
  setStatus("");
  const u = getUsername();
  if (!u) return;
  const btn = document.getElementById("btn-chat");
  try {
    const res = await withBusy(btn, "Loading…", () =>
      api("POST", "/chat/history", { username: u }),
    );
    renderChatHistory(res.history || []);
    showPanel("chat");
    document.getElementById("chat-question")?.focus();
  } catch (e) {
    setStatus(e.message, true);
  }
}

async function onChatSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  const u = getUsername();
  const input = document.getElementById("chat-question");
  const question = (input?.value || "").trim();
  if (!u || !question) return;
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    const res = await withBusy(submitBtn, "Thinking…", () =>
      api("POST", "/chat/ask", { username: u, question }),
    );
    input.value = "";
    renderChatHistory(res.history || []);
    if (res.known === false) {
      setStatus("I can only answer from the notes we have. Try asking about a tense or grammar point from Learn.", false);
    }
  } catch (e) {
    setStatus(e.message, true);
  }
}

async function onVocabClick() {
  setStatus("");
  const btn = document.getElementById("btn-vocab");
  try {
    await withBusy(btn, "Loading…", () => loadVocabList());
    showPanel("vocab");
  } catch (e) {
    setStatus(e.message, true);
  }
}

async function loadVocabList() {
  const u = getUsername();
  const res = await api("POST", "/vocab/list", { username: u });
  renderVocabList(res.items || [], res.due_count || 0);
}

function renderVocabList(items, dueCount) {
  const root = document.getElementById("vocab-root");
  root.innerHTML = "";

  const toolbar = document.createElement("div");
  toolbar.className = "vocab-toolbar";
  const due = document.createElement("p");
  due.className = "hint";
  due.textContent =
    dueCount > 0
      ? `${dueCount} word${dueCount === 1 ? "" : "s"} ready to review.`
      : "No words due right now. New words appear after writing, reading, listening, and speaking.";
  toolbar.appendChild(due);
  if (dueCount > 0) {
    const reviewBtn = document.createElement("button");
    reviewBtn.type = "button";
    reviewBtn.className = "btn btn-primary";
    reviewBtn.innerHTML = '<span class="btn-label">Review now</span>';
    reviewBtn.addEventListener("click", () => startVocabReview(reviewBtn));
    toolbar.appendChild(reviewBtn);
  }
  root.appendChild(toolbar);

  const visible = items.filter((entry) => entry.status !== "ignored");
  if (!visible.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "Your list is empty. Finish an exercise and useful words will show up here.";
    root.appendChild(empty);
    return;
  }

  const list = document.createElement("ul");
  list.className = "vocab-list";
  visible.forEach((entry) => {
    const li = document.createElement("li");
    li.className = "vocab-row";
    if (entry.starred) li.classList.add("is-starred");

    const word = document.createElement("div");
    word.className = "vocab-word";
    const lemma = document.createElement("strong");
    lemma.textContent = entry.lemma;
    const gloss = document.createElement("span");
    gloss.className = "hint";
    gloss.textContent = entry.gloss_en || "";
    word.appendChild(lemma);
    word.appendChild(gloss);

    const meta = document.createElement("span");
    meta.className = "vocab-status";
    meta.textContent = entry.status || "new";

    const actions = document.createElement("div");
    actions.className = "vocab-row-actions";
    const star = document.createElement("button");
    star.type = "button";
    star.className = "btn btn-ghost";
    star.innerHTML = `<span class="btn-label">${entry.starred ? "Unstar" : "Star"}</span>`;
    star.addEventListener("click", () => markVocab(entry.lemma, { starred: !entry.starred }));
    const ignore = document.createElement("button");
    ignore.type = "button";
    ignore.className = "btn btn-ghost";
    ignore.innerHTML = '<span class="btn-label">Ignore</span>';
    ignore.addEventListener("click", () => markVocab(entry.lemma, { status: "ignored" }));
    actions.appendChild(star);
    actions.appendChild(ignore);

    li.appendChild(word);
    li.appendChild(meta);
    li.appendChild(actions);
    list.appendChild(li);
  });
  root.appendChild(list);
}

async function markVocab(lemma, patch) {
  try {
    await api("POST", "/vocab/mark", {
      username: getUsername(),
      lemma,
      ...patch,
    });
    await loadVocabList();
  } catch (e) {
    setStatus(e.message, true);
  }
}

async function startVocabReview(btn) {
  setStatus("");
  const u = getUsername();
  try {
    const res = await withBusy(btn || null, "Loading…", () =>
      api("POST", "/vocab/review", { username: u }),
    );
    const items = res.items || [];
    if (!items.length) {
      setStatus("Nothing is due to review right now.", false);
      return;
    }
    state.vocabReview = items;
    showPanel("practice");
    updateFocusWidgetFromExercise(null);
    renderVocabReview(items);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function renderVocabReview(items) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const heading = document.getElementById("practice-heading");
  if (heading) heading.textContent = "Vocab review";

  const results = items.map((item) => ({ lemma: item.lemma, correct: null, gloss_en: item.gloss_en }));
  let idx = 0;

  const card = document.createElement("div");
  card.className = "vocab-review-card";
  const progress = document.createElement("p");
  progress.className = "hint";
  const lemmaEl = document.createElement("p");
  lemmaEl.className = "vocab-review-lemma";
  const prompt = document.createElement("p");
  prompt.className = "hint";
  prompt.textContent = "What does this mean in English?";
  const form = document.createElement("form");
  const input = document.createElement("input");
  input.type = "text";
  input.autocomplete = "off";
  input.required = true;
  input.setAttribute("aria-label", "English meaning");
  const submit = document.createElement("button");
  submit.type = "submit";
  submit.className = "btn btn-primary";
  submit.innerHTML = '<span class="btn-label">Check</span>';
  form.appendChild(input);
  form.appendChild(submit);
  const feedback = document.createElement("div");
  feedback.className = "vocab-review-feedback";
  card.appendChild(progress);
  card.appendChild(lemmaEl);
  card.appendChild(prompt);
  card.appendChild(form);
  card.appendChild(feedback);
  root.appendChild(card);

  function showItem() {
    const item = items[idx];
    progress.textContent = `${idx + 1} / ${items.length}`;
    lemmaEl.textContent = item.lemma;
    input.value = "";
    input.disabled = false;
    submit.hidden = false;
    feedback.innerHTML = "";
    input.focus();
  }

  function finish() {
    const payload = results.map(({ lemma, correct }) => ({ lemma, correct: !!correct }));
    withBusy(submit, "Saving…", () =>
      api("POST", "/vocab/review/submit", { username: getUsername(), results: payload }),
    )
      .then(() => {
        const right = payload.filter((r) => r.correct).length;
        root.innerHTML = "";
        const done = document.createElement("div");
        done.className = "feedback-block";
        const h = document.createElement("h3");
        h.textContent = "Review complete";
        done.appendChild(h);
        done.appendChild(elBlock(`${right} / ${payload.length} remembered.`));
        root.appendChild(done);
        if (heading) heading.textContent = "Practice";
        setStatus("Vocab review saved. Back to today when you're ready.", false);
      })
      .catch((e) => setStatus(e.message, true));
  }

  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const item = items[idx];
    const guess = normaliseGloss(input.value);
    const expected = normaliseGloss(item.gloss_en);
    const correct = guess.length > 0 && (guess === expected || expected.includes(guess) || guess.includes(expected));
    results[idx].correct = correct;
    input.disabled = true;
    submit.hidden = true;
    feedback.innerHTML = "";
    const badge = document.createElement("p");
    badge.className = correct ? "badge badge-ok" : "badge badge-no";
    badge.textContent = correct ? "Remembered" : "Review";
    const gloss = document.createElement("p");
    gloss.className = "passage";
    gloss.textContent = item.gloss_en;
    const next = document.createElement("button");
    next.type = "button";
    next.className = "btn btn-primary";
    next.innerHTML = `<span class="btn-label">${idx + 1 >= items.length ? "Finish" : "Next"}</span>`;
    next.addEventListener("click", () => {
      idx += 1;
      if (idx >= items.length) finish();
      else showItem();
    });
    feedback.appendChild(badge);
    feedback.appendChild(gloss);
    feedback.appendChild(next);
    next.focus();
  });

  showItem();
}

function normaliseGloss(value) {
  return String(value || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function renderListeningPractice() {
  const root = document.getElementById("practice-root");
  const prompt = state.listeningPrompt;
  root.innerHTML = "";
  root.appendChild(focusChipRow());

  const note = document.createElement("p");
  note.className = "hint";
  note.textContent = "Play the dialogue, then answer. The transcript appears after you submit.";
  root.appendChild(note);

  const player = document.createElement("audio");
  player.controls = true;
  player.className = "audio-player";
  player.src = mediaUrl(prompt.audio_url || `/audio/${prompt.clip_id}`);
  root.appendChild(player);

  const form = document.createElement("form");
  form.id = "form-listening";
  (prompt.questions || []).forEach((q, i) => {
    const wrap = document.createElement("div");
    wrap.className = "question-block";
    const lab = document.createElement("label");
    lab.htmlFor = `listening-q-${i}`;
    const prefix = document.createElement("span");
    prefix.textContent = `Question ${i + 1}: `;
    lab.appendChild(prefix);
    lab.appendChild(renderClickableSpanish(q, "", "span"));
    const inp = document.createElement("input");
    inp.type = "text";
    inp.id = `listening-q-${i}`;
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
  form.addEventListener("submit", onListeningSubmit);
  root.appendChild(form);
}

async function onListeningSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  const prompt = state.listeningPrompt;
  const answers = (prompt.questions || []).map((_, i) =>
    document.getElementById(`listening-q-${i}`).value.trim(),
  );
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    const res = await withBusy(submitBtn, "Checking answers…", () =>
      api("POST", "/listening/submit", {
        username: getUsername(),
        answers,
      }),
    );
    announceSubmission(res, "Feedback is ready below.");
    showResultsListening(res, prompt.questions || [], answers);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function showResultsListening(res, questions = [], userResponses = []) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const fb = document.createElement("div");
  fb.className = "feedback-block";

  const hTitle = document.createElement("h3");
  hTitle.textContent = "Listening — your results";
  fb.appendChild(hTitle);

  if (res.transcript) {
    const hTrans = document.createElement("h3");
    hTrans.textContent = "Transcript";
    fb.appendChild(hTrans);
    fb.appendChild(translateHint());
    fb.appendChild(renderClickableSpanish(res.transcript));
  }

  const feedback = res.feedback ?? res.correction;
  fb.appendChild(elBlock(feedback?.general_feedback ?? ""));

  const perQuestion = feedback?.individual_questions ?? [];
  const n = Math.max(questions.length, perQuestion.length, userResponses.length);
  for (let i = 0; i < n; i++) {
    const card = document.createElement("div");
    card.className = "reading-q-card";
    const hq = document.createElement("h4");
    hq.textContent = `Question ${i + 1}`;
    card.appendChild(hq);
    const promptLine = document.createElement("p");
    promptLine.className = "reading-meta";
    promptLine.innerHTML = `<strong>Prompt:</strong> ${escapeHtml(questions[i] ?? "")}`;
    card.appendChild(promptLine);
    const yourAnsLabel = document.createElement("p");
    yourAnsLabel.className = "reading-section-label";
    yourAnsLabel.textContent = "Your answer";
    card.appendChild(yourAnsLabel);
    card.appendChild(elBlock(userResponses[i] ?? ""));
    const compLabel = document.createElement("p");
    compLabel.className = "reading-section-label";
    compLabel.textContent = "Comprehension feedback";
    card.appendChild(compLabel);
    card.appendChild(elBlock(perQuestion[i] ?? ""));
    fb.appendChild(card);
  }

  appendRelatedLessons(fb, res?.lessons);
  root.appendChild(fb);
}

function renderSpeakingPractice() {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  root.appendChild(focusChipRow());

  const note = document.createElement("p");
  note.className = "hint";
  note.textContent = "Record a short answer in Spanish. We mark grammar, not pronunciation.";
  root.appendChild(note);
  root.appendChild(translateHint());
  root.appendChild(renderClickableSpanish(state.speakingPrompt || ""));

  const controls = document.createElement("div");
  controls.className = "speaking-controls";
  const recordBtn = document.createElement("button");
  recordBtn.type = "button";
  recordBtn.className = "btn btn-secondary";
  recordBtn.innerHTML = '<span class="btn-label">Record</span>';
  const statusLine = document.createElement("p");
  statusLine.className = "hint";
  statusLine.id = "speaking-status";
  controls.appendChild(recordBtn);
  controls.appendChild(statusLine);
  root.appendChild(controls);

  const form = document.createElement("form");
  form.id = "form-speaking";
  const lab = document.createElement("label");
  lab.htmlFor = "speaking-transcript";
  lab.textContent = "Transcript (edit if the capture missed a word)";
  const ta = document.createElement("textarea");
  ta.id = "speaking-transcript";
  ta.required = true;
  const submit = document.createElement("button");
  submit.type = "submit";
  submit.className = "btn btn-primary";
  submit.innerHTML = '<span class="btn-label">Submit for feedback</span>';
  form.appendChild(lab);
  form.appendChild(ta);
  form.appendChild(submit);
  form.addEventListener("submit", onSpeakingSubmit);
  root.appendChild(form);

  let recorder = null;
  let chunks = [];
  let recording = false;

  recordBtn.addEventListener("click", async () => {
    if (recording && recorder) {
      recorder.stop();
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      statusLine.textContent = "This browser cannot record audio. Type your answer in the box instead.";
      ta.focus();
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunks = [];
      const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
        ? "audio/webm;codecs=opus"
        : "audio/webm";
      recorder = new MediaRecorder(stream, { mimeType: mime });
      recorder.addEventListener("dataavailable", (ev) => {
        if (ev.data && ev.data.size) chunks.push(ev.data);
      });
      recorder.addEventListener("stop", async () => {
        recording = false;
        recordBtn.querySelector(".btn-label").textContent = "Record";
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
        if (!blob.size) {
          statusLine.textContent = "Nothing was captured. Try again, or type your answer.";
          return;
        }
        statusLine.textContent = "Transcribing…";
        try {
          const fd = new FormData();
          fd.append("username", getUsername());
          fd.append("audio", blob, "speech.webm");
          const res = await apiForm("/speaking/transcribe", fd);
          ta.value = res.transcript || "";
          statusLine.textContent = "Check the transcript, then submit.";
          ta.focus();
        } catch (e) {
          statusLine.textContent = e.message;
          setStatus(e.message, true);
        }
      });
      recorder.start();
      recording = true;
      recordBtn.querySelector(".btn-label").textContent = "Stop";
      statusLine.textContent = "Recording… tap Stop when you finish.";
    } catch (e) {
      statusLine.textContent = "Microphone permission was declined. Type your answer instead.";
      ta.focus();
    }
  });
}

async function onSpeakingSubmit(ev) {
  ev.preventDefault();
  setStatus("");
  const transcript = document.getElementById("speaking-transcript").value;
  const submitBtn = ev.target.querySelector('button[type="submit"]');
  try {
    const res = await withBusy(submitBtn, "Getting feedback…", () =>
      api("POST", "/speaking/submit", {
        username: getUsername(),
        transcript,
      }),
    );
    announceSubmission(res, "Feedback is ready below.");
    showResultsSpeaking(res, transcript);
  } catch (e) {
    setStatus(e.message, true);
  }
}

function showResultsSpeaking(res, transcript) {
  const root = document.getElementById("practice-root");
  root.innerHTML = "";
  const fb = document.createElement("div");
  fb.className = "feedback-block";
  const hSum = document.createElement("h3");
  hSum.textContent = "Summary";
  fb.appendChild(hSum);
  const note = document.createElement("p");
  note.className = "hint";
  note.textContent = "Grammar only — pronunciation is not marked.";
  fb.appendChild(note);
  const sum = res?.feedback ?? null;
  fb.appendChild(
    elBlock(
      [
        sum?.general_feedback ?? "",
        "",
        sum?.tense_edits ?? "",
        "",
        sum?.grammar_edits ?? "",
        "",
        sum?.topic_edits ?? "",
      ].join("\n"),
    ),
  );

  const hUser = document.createElement("h3");
  hUser.textContent = "Your transcript";
  fb.appendChild(hUser);
  fb.appendChild(elBlock(transcript ?? ""));

  const dc = res?.corrections ?? null;
  const hCorr = document.createElement("h3");
  hCorr.textContent = "Corrected version";
  fb.appendChild(hCorr);
  fb.appendChild(elBlock(dc?.corrected_version || ""));

  const hDetail = document.createElement("h3");
  hDetail.textContent = "Corrections in detail";
  fb.appendChild(hDetail);
  const detailWrap = document.createElement("div");
  appendEditSection(detailWrap, "Verb tenses", dc?.tense_errors);
  appendEditSection(detailWrap, "Grammar", dc?.grammar_errors);
  appendEditSection(detailWrap, "Topic / vocabulary", dc?.topic_errors);
  appendEditSection(detailWrap, "Typos & small fixes", dc?.typos);
  appendEditSection(detailWrap, "Other", dc?.other_mistakes);
  if (!detailWrap.children.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No structured edits were returned — see the summary above.";
    detailWrap.appendChild(empty);
  }
  fb.appendChild(detailWrap);
  appendRelatedLessons(fb, res?.lessons);
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
    renderProgress(res.overview);
    showPanel("progress");
    setStatus("");
  } catch (e) {
    setStatus(e.message, true);
  }
}

/**
 * Same logic as `calculate_score` in src/domain/rules/score.py
 * @param {{ total_attempts?: number, correct_attempts?: number }} stats
 * @returns {number} percentage 0–100
 */
/**
 * Feedback always shows, but a rushed or near-empty attempt does not move the
 * learner's level, so say so rather than leaving them to wonder.
 * @param {{ counted?: boolean, not_counted_reasons?: string[] }} res
 * @param {string} readyMessage
 */
function announceSubmission(res, readyMessage) {
  if (res?.counted === false) {
    const why = (res.not_counted_reasons || []).join(", and ");
    setStatus(
      why
        ? `${readyMessage} This one won't count towards your progress because ${why}.`
        : `${readyMessage} This one won't count towards your progress.`,
      false,
    );
    return;
  }
  setStatus(readyMessage, false);
}

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

/**
 * Progress reads top-down: overall level, then how each skill compares to it,
 * then the individual concepts. Labels come from the server so they match the
 * backend's wording.
 * @param {object} overview
 */
function renderProgress(overview) {
  const root = document.getElementById("progress-root");
  root.innerHTML = "";

  if (!overview) {
    root.innerHTML = '<p class="hint">No progress yet — finish an exercise to get started.</p>';
    return;
  }

  root.appendChild(renderBandSummary(overview));
  if (overview.skills?.length) root.appendChild(renderSkillBreakdown(overview.skills));
  root.appendChild(conceptTable("Tenses", overview.tenses));
  root.appendChild(conceptTable("Grammar", overview.grammar));
  root.appendChild(conceptTable("Topics", overview.topics));
}

function renderBandSummary(overview) {
  const overall = overview.overall || {};
  const wrap = document.createElement("div");
  wrap.className = "progress-block level-summary";

  const heading = document.createElement("p");
  heading.className = "level-summary-now";
  heading.textContent = `Your level: ${levelWithGloss(overall.level ?? displayLevel(overall.band), overall.gloss)}`;
  wrap.appendChild(heading);

  const detail = document.createElement("p");
  detail.className = "level-summary-goal";
  const counted = overall.genuine_attempts_at_band || 0;
  const remaining = overall.attempts_until_review;
  if (!overview.genuine_attempts) {
    detail.textContent =
      "Complete a few full exercises and we'll start tracking whether you're ready to move up.";
  } else if (remaining > 0) {
    detail.textContent = `${counted} exercise${counted === 1 ? "" : "s"} counted at this level. About ${remaining} more before we review it.`;
  } else {
    // Attempts are there, so accuracy is what's holding the level.
    detail.textContent = `You're averaging ${overall.evidence_score}% across your skills. We look for around ${overall.target_accuracy}% to move you up.`;
  }
  wrap.appendChild(detail);

  if (overview.total_attempts > overview.genuine_attempts) {
    const skipped = document.createElement("p");
    skipped.className = "progress-note";
    const diff = overview.total_attempts - overview.genuine_attempts;
    skipped.textContent = `${diff} attempt${diff === 1 ? " was" : "s were"} too short or too quick to count towards your progress.`;
    wrap.appendChild(skipped);
  }

  return wrap;
}

const RELATIVE_LEVEL_CLASS = {
  above: "pill-above",
  at: "pill-at",
  below: "pill-below",
};

function renderSkillBreakdown(skills) {
  const wrap = document.createElement("div");
  wrap.className = "progress-block";
  const h = document.createElement("h3");
  h.textContent = "By skill";
  wrap.appendChild(h);

  skills.forEach((row) => {
    const item = document.createElement("div");
    item.className = "skill-row";

    const name = document.createElement("span");
    name.className = "skill-row-name";
    name.textContent = row.label;

    const pill = document.createElement("span");
    pill.className = `skill-pill ${RELATIVE_LEVEL_CLASS[row.relative_level] || "pill-at"}`;
    pill.textContent = row.relative_label;

    const meta = document.createElement("span");
    meta.className = "skill-row-meta";
    meta.textContent = row.genuine_attempts
      ? `${row.accuracy}% over ${row.genuine_attempts} counted exercise${row.genuine_attempts === 1 ? "" : "s"}`
      : "not enough full attempts yet";

    item.appendChild(name);
    item.appendChild(pill);
    item.appendChild(meta);
    wrap.appendChild(item);
  });

  return wrap;
}

function conceptTable(title, rows) {
  const wrap = document.createElement("div");
  wrap.className = "progress-block";
  const h = document.createElement("h3");
  h.textContent = title;
  wrap.appendChild(h);

  const table = document.createElement("table");
  table.className = "progress-table";
  table.innerHTML = "<thead><tr><th>Area</th><th>Score</th></tr></thead>";
  const tb = document.createElement("tbody");

  (rows || []).forEach((row) => {
    const tr = document.createElement("tr");
    if (!row.practised) tr.className = "progress-row-untouched";

    const name = document.createElement("td");
    name.textContent = row.label;

    const score = document.createElement("td");
    score.className = "progress-score-cell";
    score.textContent = row.practised
      ? `${Math.round(row.score * 10) / 10}%`
      : "not practised";

    tr.appendChild(name);
    tr.appendChild(score);
    tb.appendChild(tr);
  });

  table.appendChild(tb);
  wrap.appendChild(table);
  return wrap;
}

function onBackExercise() {
  state.exercise = null;
  state.writingPrompt = null;
  state.readingPrompt = null;
  state.drills = null;
  state.listeningPrompt = null;
  state.speakingPrompt = null;
  state.vocabReview = null;
  const heading = document.getElementById("practice-heading");
  if (heading) heading.textContent = "Practice";
  updateFocusWidgetFromExercise(null);
  document.getElementById("practice-root").innerHTML = "";
  setStatus("Back to today.", false);
  goHome();
}

function onLogout() {
  clearSession();
  state.exercise = null;
  state.writingPrompt = null;
  state.readingPrompt = null;
  state.drills = null;
  state.listeningPrompt = null;
  state.speakingPrompt = null;
  state.vocabReview = null;
  const heading = document.getElementById("practice-heading");
  if (heading) heading.textContent = "Practice";
  updateFocusWidgetFromExercise(null);
  document.getElementById("practice-root").innerHTML = "";
  document.getElementById("progress-root").innerHTML = "";
  const rec = document.getElementById("daily-root");
  if (rec) rec.innerHTML = "";
  const extras = document.getElementById("extras-root");
  if (extras) extras.innerHTML = "";
  const learn = document.getElementById("learn-root");
  if (learn) learn.innerHTML = "";
  const chat = document.getElementById("chat-root");
  if (chat) chat.innerHTML = "";
  const vocab = document.getElementById("vocab-root");
  if (vocab) vocab.innerHTML = "";
  const lookup = document.getElementById("lookup-result");
  if (lookup) {
    lookup.hidden = true;
    lookup.innerHTML = "";
  }
  const lookupInput = document.getElementById("lookup-word");
  if (lookupInput) lookupInput.value = "";
  setWalkthroughAllowed(false);
  syncProgressUnlock(0);
  setStatus("Logged out.", false);
  showPanel("login");
}

function init() {
  ensureFocusWidget();
  const prefTenses = document.getElementById("pref-tenses");
  const prefGrammar = document.getElementById("pref-grammar");
  const prefTopics = document.getElementById("pref-topics");
  buildCheckboxGrid(prefTenses, TENSE_OPTS, "pref-tense");
  buildCheckboxGrid(prefGrammar, GRAMMAR_OPTS, "pref-grammar");
  buildCheckboxGrid(prefTopics, TOPIC_OPTS, "pref-topic");

  document.getElementById("form-login").addEventListener("submit", onLogin);
  document.getElementById("form-goals").addEventListener("submit", onGoalsSubmit);
  document.getElementById("form-placement").addEventListener("submit", onPlacementSubmit);
  document.getElementById("form-exercise").addEventListener("submit", onExerciseSubmit);
  document.getElementById("btn-logout").addEventListener("click", onLogout);
  document.getElementById("btn-goals-logout").addEventListener("click", onLogout);
  document.getElementById("btn-placement-logout").addEventListener("click", onLogout);
  document.getElementById("btn-progress").addEventListener("click", onProgressClick);
  document.getElementById("btn-learn").addEventListener("click", onLearnClick);
  document.getElementById("btn-chat").addEventListener("click", onChatClick);
  document.getElementById("btn-vocab").addEventListener("click", onVocabClick);
  document.getElementById("form-chat").addEventListener("submit", onChatSubmit);
  document.getElementById("form-lookup").addEventListener("submit", onLookupSubmit);
  document.getElementById("btn-back-exercise").addEventListener("click", onBackExercise);
  document.getElementById("btn-close-progress").addEventListener("click", goHome);
  document.getElementById("btn-close-learn").addEventListener("click", goHome);
  document.getElementById("btn-close-chat").addEventListener("click", goHome);
  document.getElementById("btn-close-vocab").addEventListener("click", goHome);

  document.getElementById("btn-help").addEventListener("click", () => {
    const p = helpPanelEl();
    if (!p) return;
    p.classList.toggle("hidden");
  });
  document.getElementById("help-close").addEventListener("click", closeHelpPanel);
  document.getElementById("help-walkthrough").addEventListener("click", openWalkthrough);
  document.getElementById("walkthrough-close").addEventListener("click", closeWalkthrough);
  document.getElementById("walkthrough-back").addEventListener("click", () => {
    walkthroughIdx = Math.max(0, walkthroughIdx - 1);
    renderWalkthroughStep();
  });
  document.getElementById("walkthrough-next").addEventListener("click", () => {
    if (walkthroughIdx >= WALKTHROUGH_STEPS.length - 1) {
      closeWalkthrough();
      return;
    }
    walkthroughIdx += 1;
    renderWalkthroughStep();
  });
  document.getElementById("walkthrough-overlay").addEventListener("click", (ev) => {
    if (ev.target && ev.target.id === "walkthrough-overlay") closeWalkthrough();
  });
  document.addEventListener("click", (ev) => {
    const pop = wordPopoverEl();
    if (!pop || pop.classList.contains("hidden")) return;
    if (pop.contains(ev.target) || ev.target.closest(".word-hit")) return;
    closeWordPopover();
  });
  document.addEventListener("keydown", (ev) => {
    if (ev.key !== "Escape") return;
    closeHelpPanel();
    closeWalkthrough();
    closeWordPopover();
  });

  document.querySelectorAll('input[name="style"]').forEach((r) => {
    r.addEventListener("change", onStyleChange);
  });

  document.getElementById("ex-type").addEventListener("change", () => {
    syncPreferencePanels();
  });

  document.querySelectorAll('input[name="drill-pref-axis"]').forEach((r) => {
    r.addEventListener("change", () => {
      const style = document.querySelector('input[name="style"]:checked').value;
      if (style === "preferences") rebuildDrillPrefGrid();
    });
  });

  const resuming = getUsername();
  if (resuming) {
    updateExerciseUserLabel();
    showPanel("exercise");
    // A returning session may still owe us onboarding, so ask the server.
    api("GET", `/onboarding/status?username=${encodeURIComponent(resuming)}`)
      .then((res) => routeToStep(res.step))
      .catch(() => showPanel("login"));
  } else {
    showPanel("login");
  }

  syncPreferencePanels();
}

document.addEventListener("DOMContentLoaded", init);
