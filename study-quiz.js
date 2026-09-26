/**
 * Shared practice-quiz engine for CompTIA study guides.
 * Expects window.QUIZ_DATA = { title, sections, terms }.
 * Optional term.scenario enables "scenario" mode (prompt is a made-up ticket).
 */
(function () {
  "use strict";

  const state = {
    pool: [],
    questions: [],
    index: 0,
    correct: 0,
    answered: false,
    mode: "term-to-def",
    missed: [],
    inChaptersOnly: false,
  };

  function $(sel) {
    return document.querySelector(sel);
  }

  function supportsChapterFilter() {
    return Boolean(window.QUIZ_DATA?.supportsChapterFilter);
  }

  function termsHaveScenarios() {
    return (window.QUIZ_DATA.terms || []).some((t) => t.scenario);
  }

  function selectedMode() {
    return document.querySelector('input[name="quiz-mode"]:checked')?.value || "term-to-def";
  }

  function isScenarioMode() {
    return selectedMode() === "scenario";
  }

  function sectionCount(section) {
    if (state.inChaptersOnly && typeof section.coreCount === "number") {
      return section.coreCount;
    }
    return section.count;
  }

  function visibleTerms() {
    const terms = window.QUIZ_DATA.terms || [];
    if (!state.inChaptersOnly) return terms;
    return terms.filter((t) => t.inChapters);
  }

  function visibleTotal() {
    if (state.inChaptersOnly && typeof window.QUIZ_DATA.coreTotal === "number") {
      return window.QUIZ_DATA.coreTotal;
    }
    return window.QUIZ_DATA.total;
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function truncate(text, max) {
    if (text.length <= max) return text;
    return text.slice(0, max - 1).trim() + "…";
  }

  function pickDistractors(term, pool, count, mode) {
    const nameKey = (term.name || "").trim().toLowerCase();
    let rest = pool.filter((t) => t.id !== term.id && (t.name || "").trim().toLowerCase() !== nameKey);
    if (mode === "scenario" && term.role) {
      const sameRole = rest.filter((t) => t.role === term.role);
      if (sameRole.length) rest = sameRole;
    }
    const same = rest.filter((t) => t.section === term.section);
    const other = rest.filter((t) => t.section !== term.section);
    const candidates = shuffle(same.length >= count ? same : same.concat(other));
    return candidates.slice(0, count);
  }

  function buildQuestions(terms, mode, distractorPool) {
    const pool = distractorPool && distractorPool.length ? distractorPool : terms;
    return shuffle(terms).map((term) => {
      const distractors = pickDistractors(term, pool, 3, mode);
      const choices =
        mode === "term-to-def"
          ? shuffle([
              { text: term.definition, correct: true },
              ...distractors.map((d) => ({ text: d.definition, correct: false })),
            ])
          : shuffle([
              { text: term.name, correct: true },
              ...distractors.map((d) => ({ text: d.name, correct: false })),
            ]);
      return { term, choices, mode };
    });
  }

  function showScreen(id) {
    document.querySelectorAll("[data-screen]").forEach((el) => {
      el.hidden = el.dataset.screen !== id;
    });
  }

  function categorySlug(value) {
    return (value || "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
  }

  function termMatchesCategory(term, wanted) {
    if (!wanted) return true;
    const cat = (term.category || "").trim().toLowerCase();
    const needle = wanted.trim().toLowerCase();
    return cat === needle || categorySlug(cat) === categorySlug(needle) || cat.includes(needle);
  }

  function getUrlParams() {
    const p = new URLSearchParams(window.location.search);
    const section = p.get("section");
    const sections = p.get("sections");
    return {
      sections: section
        ? [section]
        : sections
          ? sections.split(",").map((s) => s.trim()).filter(Boolean)
          : [],
      start: p.get("start") === "1",
      mode: p.get("mode") || null,
      core: p.get("core") === "1",
      category: p.get("category") || "",
    };
  }

  function setSectionSelection(ids) {
    document.querySelectorAll("#section-toggles input").forEach((el) => {
      el.checked = ids.length ? ids.includes(el.value) : true;
    });
  }

  function renderSetup() {
    const container = $("#section-filters");
    if (!container) return;
    container.innerHTML = "";
    window.QUIZ_DATA.sections.forEach((s) => {
      const count = sectionCount(s);
      const card = document.createElement("button");
      card.type = "button";
      card.className = "section-card" + (count < 4 ? " is-empty" : "");
      card.dataset.section = s.id;
      card.disabled = count < 4;
      const kind = isScenarioMode() ? (count === 1 ? "scenario" : "scenarios") : count === 1 ? "term" : "terms";
      card.innerHTML = `<span class="section-card-id">${s.id}</span><span class="section-card-title">${s.title}</span><span class="section-card-count">${count} ${kind}</span>`;
      card.addEventListener("click", () => startQuiz([s.id]));
      container.appendChild(card);
    });
    const termCount = $("#term-count");
    if (termCount) termCount.textContent = visibleTotal();
    const kind = $("#pool-kind");
    if (kind) kind.textContent = isScenarioMode() ? "scenarios" : "terms";
    const allBtn = $("#start-all-btn");
    if (allBtn) allBtn.textContent = isScenarioMode() ? "Quiz all scenarios" : "Quiz all sections";
    updateSetupHeading(getSelectedSections());
  }

  function updateSetupHeading(sections) {
    const el = $("#setup-focus");
    if (!el) return;
    const focusHint = state.inChaptersOnly
      ? "Filtering to terms also mentioned in Chapters 1–4. "
      : "";
    if (!sections || !sections.length) {
      el.textContent =
        focusHint +
        (window.QUIZ_DATA.chapter === 5
          ? "Pick a letter range below to start instantly, or customize with checkboxes."
          : isScenarioMode()
            ? "Each term has a made-up help-desk ticket. Pick a section, or quiz the whole chapter."
            : "Pick a section below to start instantly, or customize with checkboxes.");
      return;
    }
    const labels = sections.map((id) => {
      const s = window.QUIZ_DATA.sections.find((x) => x.id === id);
      return s ? `${s.id} (${sectionCount(s)})` : id;
    });
    el.textContent = `${focusHint}Ready: ${labels.join(", ")}`;
  }

  function renderSectionToggles() {
    const container = $("#section-toggles");
    if (!container) return;
    container.innerHTML = "";
    window.QUIZ_DATA.sections.forEach((s) => {
      const count = sectionCount(s);
      const label = document.createElement("label");
      label.className = "check-pill";
      label.hidden = state.inChaptersOnly && count === 0;
      label.innerHTML = `<input type="checkbox" value="${s.id}" ${count ? "checked" : ""} ${count < 4 ? "disabled" : ""}> <span>${s.title || s.id}</span> <em>(${count})</em>`;
      label.querySelector("input").addEventListener("change", () => {
        updateSetupHeading(getSelectedSections());
      });
      container.appendChild(label);
    });
  }

  function syncChapterFilterUi() {
    const row = $("#chapter-filter-row");
    const checkbox = $("#filter-core");
    const hint = $("#filter-core-hint");
    if (!supportsChapterFilter()) {
      if (row) row.hidden = true;
      return;
    }
    if (row) row.hidden = false;
    if (checkbox) checkbox.checked = state.inChaptersOnly;
    if (hint) {
      const core = window.QUIZ_DATA.coreTotal ?? 0;
      const total = window.QUIZ_DATA.total ?? 0;
      hint.textContent = state.inChaptersOnly
        ? `Using ${core} of ${total} acronyms`
        : `${core} of ${total} appear in other chapters`;
    }
  }

  function setInChaptersOnly(on) {
    state.inChaptersOnly = Boolean(on);
    syncChapterFilterUi();
    renderSetup();
    renderSectionToggles();
  }

  function getSelectedSections() {
    return [...document.querySelectorAll("#section-toggles input:checked:not(:disabled)")].map(
      (el) => el.value
    );
  }

  function startableSections() {
    return window.QUIZ_DATA.sections.filter((s) => sectionCount(s) >= 4).map((s) => s.id);
  }

  function startQuiz(forcedSections, forcedCategory) {
    const sections = forcedSections || getSelectedSections();
    if (!sections.length) {
      alert("Select at least one section.");
      return;
    }
    const category = forcedCategory !== undefined ? forcedCategory : getUrlParams().category;
    state.mode = selectedMode();
    const sectionPool = visibleTerms().filter((t) => sections.includes(t.section));
    state.pool = category ? sectionPool.filter((t) => termMatchesCategory(t, category)) : sectionPool;
    if (state.mode === "scenario") {
      state.pool = state.pool.filter((t) => t.scenario || t.definition);
    }
    if (state.pool.length < 4) {
      alert("Need at least 4 terms in the selected sections for multiple-choice questions.");
      return;
    }
    state.questions = buildQuestions(state.pool, state.mode, sectionPool);
    state.index = 0;
    state.correct = 0;
    state.missed = [];
    showScreen("quiz");
    renderQuestion();
  }

  function renderQuestion() {
    const q = state.questions[state.index];
    const total = state.questions.length;
    state.answered = false;

    $("#progress-label").textContent = `Question ${state.index + 1} of ${total}`;
    $("#progress-fill").style.width = `${(state.index / total) * 100}%`;
    $("#score-live").textContent = `${state.correct} correct`;

    const badge = $("#section-badge");
    badge.textContent = q.term.section;
    badge.title = q.term.sectionTitle;

    const categoryEl = $("#category-label");
    if (categoryEl) {
      const category = q.term.category || q.term.sectionTitle || "";
      categoryEl.textContent = category;
      categoryEl.hidden = !category;
    }

    const prompt = $("#prompt-text");
    prompt.classList.toggle("is-scenario", q.mode === "scenario");
    if (q.mode === "term-to-def") {
      $("#prompt-label").textContent = "Which definition best describes this term?";
      prompt.textContent = q.term.name;
    } else if (q.mode === "scenario") {
      $("#prompt-label").textContent = "Which term, tool, or command fits this scenario?";
      prompt.textContent = q.term.scenario || q.term.definition;
    } else {
      $("#prompt-label").textContent = "Which term matches this definition?";
      prompt.textContent = q.term.definition;
    }

    const choicesEl = $("#choices");
    choicesEl.innerHTML = "";
    $("#feedback").hidden = true;
    $("#next-btn").hidden = true;

    q.choices.forEach((choice) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice";
      btn.textContent = truncate(choice.text, q.mode === "term-to-def" ? 220 : 160);
      btn.title = choice.text;
      btn.addEventListener("click", () => selectAnswer(btn, choice.correct, q));
      choicesEl.appendChild(btn);
    });
  }

  function selectAnswer(btn, isCorrect, q) {
    if (state.answered) return;
    state.answered = true;

    document.querySelectorAll(".choice").forEach((b) => {
      b.disabled = true;
      if (b === btn) b.classList.add(isCorrect ? "right" : "wrong");
    });

    const correctBtn = [...document.querySelectorAll(".choice")].find((b, i) => q.choices[i].correct);
    if (correctBtn && correctBtn !== btn) correctBtn.classList.add("right");

    if (isCorrect) {
      state.correct++;
    } else {
      state.missed.push(q);
    }

    const fb = $("#feedback");
    fb.hidden = false;
    fb.className = "feedback " + (isCorrect ? "good" : "bad");
    const context = [q.term.section, q.term.category].filter(Boolean).join(" · ");
    fb.innerHTML = isCorrect
      ? `<strong>Correct!</strong> ${context} — <em>${q.term.name}</em>`
      : `<strong>Not quite.</strong> The answer was <em>${q.term.name}</em>.<br><span class="def-review">${q.term.definition}</span>`;

    $("#score-live").textContent = `${state.correct} correct`;
    $("#next-btn").hidden = false;
    $("#next-btn").textContent = state.index + 1 >= state.questions.length ? "See results" : "Next question";
  }

  function nextQuestion() {
    if (state.index + 1 >= state.questions.length) {
      showResults();
      return;
    }
    state.index++;
    renderQuestion();
  }

  function showResults() {
    showScreen("results");
    const total = state.questions.length;
    const pct = Math.round((state.correct / total) * 100);
    $("#results-score").textContent = `${state.correct} / ${total}`;
    $("#results-pct").textContent = `${pct}%`;

    const review = $("#review-list");
    review.innerHTML = "";
    if (!state.missed.length) {
      review.innerHTML = `<p class="all-good">Perfect score — you nailed every ${state.mode === "scenario" ? "scenario" : "term"}!</p>`;
      return;
    }
    state.missed.forEach((q) => {
      const item = document.createElement("div");
      item.className = "review-item";
      const context = [q.term.section, q.term.category].filter(Boolean).join(" · ");
      const extra = q.mode === "scenario" && q.term.scenario ? `<p>${q.term.scenario}</p>` : "";
      item.innerHTML = `<div class="review-meta">${context}</div><strong>${q.term.name}</strong>${extra}<p>${q.term.definition}</p>`;
      review.appendChild(item);
    });
  }

  function retryMissed() {
    if (!state.missed.length) return;
    state.questions = buildQuestions(
      state.missed.map((q) => q.term),
      state.mode
    );
    state.index = 0;
    state.correct = 0;
    state.missed = [];
    showScreen("quiz");
    renderQuestion();
  }

  function init() {
    if (!window.QUIZ_DATA) {
      document.body.innerHTML = "<p style='padding:2rem'>Quiz data not loaded.</p>";
      return;
    }

    const params = getUrlParams();
    if (supportsChapterFilter()) {
      state.inChaptersOnly = params.core;
      syncChapterFilterUi();
      $("#filter-core")?.addEventListener("change", (e) => {
        setInChaptersOnly(e.target.checked);
      });
    }

    if (params.mode) {
      const modeInput = document.querySelector(`input[name="quiz-mode"][value="${params.mode}"]`);
      if (modeInput) modeInput.checked = true;
    }

    const scenarioRadio = document.querySelector('input[name="quiz-mode"][value="scenario"]');
    if (scenarioRadio && !termsHaveScenarios()) scenarioRadio.closest("label")?.remove();
    document.querySelectorAll('input[name="quiz-mode"]').forEach((el) => {
      el.addEventListener("change", () => {
        renderSetup();
        renderSectionToggles();
      });
    });

    renderSetup();
    renderSectionToggles();
    $("#start-btn")?.addEventListener("click", () => startQuiz());
    $("#start-all-btn")?.addEventListener("click", () => {
      const all = startableSections();
      setSectionSelection(all);
      startQuiz(all);
    });
    $("#next-btn")?.addEventListener("click", nextQuestion);
    $("#retry-btn")?.addEventListener("click", retryMissed);
    $("#restart-btn")?.addEventListener("click", () => showScreen("setup"));

    if (params.sections.length) {
      setSectionSelection(params.sections);
      updateSetupHeading(params.sections);
      if (params.start) {
        startQuiz(params.sections, params.category);
        return;
      }
    } else if (params.start) {
      startQuiz(startableSections());
      return;
    }
    showScreen("setup");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
