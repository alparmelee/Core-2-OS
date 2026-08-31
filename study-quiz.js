/**
 * Shared practice-quiz engine for CompTIA study guides.
 * Expects window.QUIZ_DATA = { title, sections, terms }.
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
  };

  function $(sel) {
    return document.querySelector(sel);
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

  function pickDistractors(term, pool, count) {
    const same = pool.filter((t) => t.id !== term.id && t.section === term.section);
    const other = pool.filter((t) => t.id !== term.id && t.section !== term.section);
    const candidates = shuffle(same.length >= count ? same : same.concat(other));
    return candidates.slice(0, count);
  }

  function buildQuestions(terms, mode) {
    return shuffle(terms).map((term) => {
      const distractors = pickDistractors(term, terms, 3);
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
    };
  }

  function setSectionSelection(ids) {
    document.querySelectorAll("#section-filters input").forEach((el) => {
      el.checked = ids.length ? ids.includes(el.value) : true;
    });
  }

  function renderSetup() {
    const container = $("#section-filters");
    if (!container) return;
    container.innerHTML = "";
    window.QUIZ_DATA.sections.forEach((s) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "section-card";
      card.dataset.section = s.id;
      card.innerHTML = `<span class="section-card-id">${s.id}</span><span class="section-card-title">${s.title}</span><span class="section-card-count">${s.count} terms</span>`;
      card.addEventListener("click", () => startQuiz([s.id]));
      container.appendChild(card);
    });
    $("#term-count").textContent = window.QUIZ_DATA.total;
    updateSetupHeading();
  }

  function updateSetupHeading(sections) {
    const el = $("#setup-focus");
    if (!el) return;
    if (!sections || !sections.length) {
      el.textContent = "Pick a section below to start instantly, or customize with checkboxes.";
      return;
    }
    const labels = sections.map((id) => {
      const s = window.QUIZ_DATA.sections.find((x) => x.id === id);
      return s ? `${s.id} (${s.count})` : id;
    });
    el.textContent = `Ready: ${labels.join(", ")}`;
  }

  function renderSectionToggles() {
    const container = $("#section-toggles");
    if (!container) return;
    container.innerHTML = "";
    window.QUIZ_DATA.sections.forEach((s) => {
      const label = document.createElement("label");
      label.className = "check-pill";
      label.innerHTML = `<input type="checkbox" value="${s.id}" checked> <span>${s.id}</span> <em>(${s.count})</em>`;
      label.querySelector("input").addEventListener("change", () => {
        updateSetupHeading(getSelectedSections());
      });
      container.appendChild(label);
    });
  }

  function getSelectedSections() {
    return [...document.querySelectorAll("#section-toggles input:checked")].map((el) => el.value);
  }

  function startQuiz(forcedSections) {
    const sections = forcedSections || getSelectedSections();
    if (!sections.length) {
      alert("Select at least one section.");
      return;
    }
    state.mode = document.querySelector('input[name="quiz-mode"]:checked')?.value || "term-to-def";
    state.pool = window.QUIZ_DATA.terms.filter((t) => sections.includes(t.section));
    if (state.pool.length < 4) {
      alert("Need at least 4 terms in the selected sections for multiple-choice questions.");
      return;
    }
    state.questions = buildQuestions(state.pool, state.mode);
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
    $("#progress-fill").style.width = `${((state.index) / total) * 100}%`;
    $("#score-live").textContent = `${state.correct} correct`;

    const badge = $("#section-badge");
    badge.textContent = q.term.section;
    badge.title = q.term.sectionTitle;

    if (q.mode === "term-to-def") {
      $("#prompt-label").textContent = "Which definition best describes this term?";
      $("#prompt-text").textContent = q.term.name;
    } else {
      $("#prompt-label").textContent = "Which term matches this definition?";
      $("#prompt-text").textContent = q.term.definition;
    }

    const choicesEl = $("#choices");
    choicesEl.innerHTML = "";
    $("#feedback").hidden = true;
    $("#next-btn").hidden = true;

    q.choices.forEach((choice, i) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "choice";
      btn.textContent = truncate(choice.text, 220);
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
    fb.innerHTML = isCorrect
      ? `<strong>Correct!</strong> ${q.term.section} — <em>${q.term.name}</em>`
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
      review.innerHTML = '<p class="all-good">Perfect score — you nailed every term!</p>';
      return;
    }
    state.missed.forEach((q) => {
      const item = document.createElement("div");
      item.className = "review-item";
      item.innerHTML = `<div class="review-meta">${q.term.section}</div><strong>${q.term.name}</strong><p>${q.term.definition}</p>`;
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
    renderSetup();
    renderSectionToggles();
    $("#start-btn")?.addEventListener("click", () => startQuiz());
    $("#start-all-btn")?.addEventListener("click", () => {
      const all = window.QUIZ_DATA.sections.map((s) => s.id);
      setSectionSelection(all);
      startQuiz(all);
    });
    $("#next-btn")?.addEventListener("click", nextQuestion);
    $("#retry-btn")?.addEventListener("click", retryMissed);
    $("#restart-btn")?.addEventListener("click", () => showScreen("setup"));

    const params = getUrlParams();
    if (params.mode) {
      const modeInput = document.querySelector(`input[name="quiz-mode"][value="${params.mode}"]`);
      if (modeInput) modeInput.checked = true;
    }
    if (params.sections.length) {
      setSectionSelection(params.sections);
      updateSetupHeading(params.sections);
      if (params.start) {
        startQuiz(params.sections);
        return;
      }
    } else if (params.start) {
      const all = window.QUIZ_DATA.sections.map((s) => s.id);
      startQuiz(all);
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
