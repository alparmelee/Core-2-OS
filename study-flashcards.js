/**
 * Flashcard mode for study guides.
 * Front: category + term. Order follows the page.
 * Loaded by study-editor.js (or include this script directly).
 */
(function () {
  "use strict";
  if (window.__studyFlashcards) return;
  window.__studyFlashcards = true;

  const style = document.createElement("style");
  style.setAttribute("data-study-flashcards", "1");
  style.textContent = `
    .study-fc-open{ overflow:hidden; }
    .study-fc-overlay{
      position:fixed; inset:0; z-index:1400;
      display:flex; flex-direction:column; align-items:center; justify-content:center;
      padding:1.2rem 1.2rem 5.5rem;
      background:rgba(10,16,24,0.88);
      backdrop-filter:blur(10px);
      color:#f8fafc;
      font-family:"Sora",system-ui,sans-serif;
    }
    .study-fc-overlay[hidden]{ display:none !important; }
    .study-fc-top{
      width:min(640px, 100%);
      display:flex; align-items:center; justify-content:space-between;
      gap:0.8rem; margin-bottom:0.9rem;
    }
    .study-fc-progress{ font-size:0.82rem; font-weight:600; color:#cbd5e1; letter-spacing:0.04em; }
    .study-fc-close{
      border:0; background:rgba(255,255,255,0.12); color:#fff;
      width:2.4rem; height:2.4rem; border-radius:999px; cursor:pointer; font-size:1.3rem; line-height:1;
    }
    .study-fc-close:hover{ background:rgba(255,255,255,0.22); }
    .study-fc-card{
      width:min(640px, 100%);
      min-height:min(52vh, 380px);
      background:#fff; color:#121820;
      border-radius:22px;
      box-shadow:0 24px 80px rgba(0,0,0,0.4);
      padding:2rem 2.1rem;
      cursor:pointer;
      display:flex; flex-direction:column; justify-content:center;
      text-align:center;
    }
    .study-fc-card:focus{ outline:3px solid #5eead4; outline-offset:4px; }
    .study-fc-cat{
      font-size:0.72rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
      color:#0f766e; margin:0 0 0.85rem;
    }
    .study-fc-term{
      font-family:"Fraunces",Georgia,serif;
      font-size:clamp(1.6rem, 4vw, 2.35rem);
      font-weight:700; letter-spacing:-0.02em; line-height:1.15;
      margin:0;
    }
    .study-fc-hint{ margin:1.2rem 0 0; font-size:0.82rem; color:#64748b; }
    .study-fc-back{ text-align:left; overflow:auto; max-height:min(56vh, 420px); }
    .study-fc-back .aka{
      display:inline-block; font-size:0.78rem; font-weight:600;
      color:#0e4d7b; background:rgba(14,77,123,0.08);
      padding:0.18rem 0.55rem; border-radius:999px; margin:0 0 0.65rem;
    }
    .study-fc-back p{ margin:0 0 0.7rem; line-height:1.55; }
    .study-fc-back p:last-child{ margin-bottom:0; }
    .study-fc-back ul, .study-fc-back ol{ margin:0.4rem 0 0.7rem; padding-left:1.2rem; }
    .study-fc-back .demo, .study-fc-back .note{
      margin:0.75rem 0 0; padding:0.75rem 0.9rem;
      border-left:4px solid #0f766e; background:rgba(15,118,110,0.08);
      border-radius:0 10px 10px 0; color:#4a5568; font-size:0.9rem;
    }
    .study-fc-back .primary-route, .study-fc-back .txt{ display:block; margin-top:0.35rem; }
    .study-fc-back code{
      font-family:"Cascadia Mono",Consolas,monospace; font-size:0.86em;
      background:rgba(18,24,32,0.06); border-radius:5px; padding:0.05rem 0.35rem;
    }
    .study-fc-back img{ max-width:100%; height:auto; border-radius:10px; }
    .study-fc-nav{
      width:min(640px, 100%);
      display:flex; gap:0.55rem; justify-content:center; flex-wrap:wrap;
      margin-top:1rem;
    }
    .study-fc-nav button{
      font:600 0.88rem/1 "Sora",system-ui,sans-serif;
      border:0; border-radius:999px; padding:0.7rem 1.15rem; cursor:pointer;
      background:#e2e8f0; color:#0f172a;
    }
    .study-fc-nav button.primary{ background:#0f766e; color:#fff; }
    .study-fc-nav button:disabled{ opacity:0.4; cursor:default; }
    .study-edit-bar button[data-flashcards]{ background:#99f6e4; color:#115e59; }
  `;
  document.head.appendChild(style);

  function text(el) {
    return (el && el.textContent ? el.textContent : "").replace(/\s+/g, " ").trim();
  }

  function categoryFor(el) {
    const section = el.closest("section");
    const group = el.closest(".qr-group");
    const parts = [];
    if (section) {
      const eyebrow = section.querySelector(".section-head .eyebrow");
      const h2 = section.querySelector(".section-head h2");
      if (eyebrow) parts.push(text(eyebrow));
      if (h2) parts.push(text(h2));
    }
    if (group) {
      const gh = group.querySelector(":scope > h3");
      if (gh) parts.push(text(gh));
    }
    return parts.filter(Boolean).join(" — ");
  }

  function cloneBack(nodes, skipSel) {
    const wrap = document.createElement("div");
    nodes.forEach((n) => {
      if (n.nodeType === 1 && skipSel && n.matches(skipSel)) return;
      if (n.nodeType === 1 && n.matches(".study-add-p")) return;
      wrap.appendChild(n.cloneNode(true));
    });
    return wrap.innerHTML.trim();
  }

  function collectCards() {
    const cards = [];
    document.querySelectorAll("article.term, article.nav-card, .qr-list li").forEach((el) => {
      if (el.matches("article.term")) {
        const body = el.querySelector(".body") || el;
        const h3 = body.querySelector("h3");
        const term = text(h3) || text(el.querySelector(".glyph")) || el.id || "Term";
        const backHTML = cloneBack(Array.from(body.childNodes), "h3");
        if (!term && !backHTML) return;
        cards.push({ category: categoryFor(el), term, backHTML });
        return;
      }
      if (el.matches("article.nav-card")) {
        const term = text(el.querySelector("h3"));
        const bits = [];
        const route = el.querySelector(".primary-route");
        if (route) bits.push(route.outerHTML);
        const details = el.querySelector("details.alt");
        if (details) bits.push(details.outerHTML);
        if (!term) return;
        cards.push({ category: categoryFor(el), term, backHTML: bits.join("") });
        return;
      }
      const term = text(el.querySelector(".qr-name")) || text(el);
      const path = el.querySelector(".qr-path");
      cards.push({
        category: categoryFor(el),
        term,
        backHTML: path ? path.innerHTML : el.innerHTML,
      });
    });
    return cards;
  }

  const overlay = document.createElement("div");
  overlay.className = "study-fc-overlay";
  overlay.hidden = true;
  overlay.setAttribute("data-study-flashcards", "1");
  overlay.innerHTML =
    '<div class="study-fc-top">' +
    '<span class="study-fc-progress" data-fc-progress></span>' +
    '<button type="button" class="study-fc-close" data-fc-close aria-label="Close">✕</button>' +
    "</div>" +
    '<div class="study-fc-card" data-fc-card tabindex="0" role="button" aria-label="Flip card"></div>' +
    '<div class="study-fc-nav">' +
    '<button type="button" data-fc-prev>← Previous</button>' +
    '<button type="button" class="primary" data-fc-flip>Flip</button>' +
    '<button type="button" data-fc-next>Next →</button>' +
    "</div>";
  document.body.appendChild(overlay);

  const cardEl = overlay.querySelector("[data-fc-card]");
  const progressEl = overlay.querySelector("[data-fc-progress]");
  const prevBtn = overlay.querySelector("[data-fc-prev]");
  const nextBtn = overlay.querySelector("[data-fc-next]");
  const flipBtn = overlay.querySelector("[data-fc-flip]");

  let cards = [];
  let index = 0;
  let showingBack = false;

  function render() {
    const c = cards[index];
    if (!c) return;
    progressEl.textContent = index + 1 + " / " + cards.length;
    prevBtn.disabled = index === 0;
    nextBtn.disabled = index === cards.length - 1;
    if (!showingBack) {
      cardEl.innerHTML =
        (c.category ? '<p class="study-fc-cat"></p>' : "") +
        '<h2 class="study-fc-term"></h2>' +
        '<p class="study-fc-hint">Click or press Space to flip</p>';
      const cat = cardEl.querySelector(".study-fc-cat");
      if (cat) cat.textContent = c.category;
      cardEl.querySelector(".study-fc-term").textContent = c.term;
    } else {
      cardEl.innerHTML =
        (c.category ? '<p class="study-fc-cat"></p>' : "") +
        '<h2 class="study-fc-term"></h2>' +
        '<div class="study-fc-back"></div>';
      const cat = cardEl.querySelector(".study-fc-cat");
      if (cat) cat.textContent = c.category;
      cardEl.querySelector(".study-fc-term").textContent = c.term;
      cardEl.querySelector(".study-fc-back").innerHTML = c.backHTML || "<p>No notes on this term.</p>";
    }
  }

  function openAt(i) {
    cards = collectCards();
    if (!cards.length) return;
    index = Math.max(0, Math.min(i || 0, cards.length - 1));
    showingBack = false;
    overlay.hidden = false;
    document.body.classList.add("study-fc-open");
    render();
    cardEl.focus();
  }

  function close() {
    overlay.hidden = true;
    document.body.classList.remove("study-fc-open");
  }

  function flip() {
    showingBack = !showingBack;
    render();
  }

  function go(delta) {
    const next = index + delta;
    if (next < 0 || next >= cards.length) return;
    index = next;
    showingBack = false;
    render();
  }

  cardEl.addEventListener("click", flip);
  flipBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    flip();
  });
  prevBtn.addEventListener("click", () => go(-1));
  nextBtn.addEventListener("click", () => go(1));
  overlay.querySelector("[data-fc-close]").addEventListener("click", close);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });

  document.addEventListener("keydown", (e) => {
    if (overlay.hidden) return;
    if (e.key === "Escape") {
      e.preventDefault();
      close();
    } else if (e.key === " " || e.key === "Enter") {
      e.preventDefault();
      flip();
    } else if (e.key === "ArrowRight" || e.key === "ArrowDown") {
      e.preventDefault();
      go(1);
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
      e.preventDefault();
      go(-1);
    }
  });

  function addButton() {
    if (!collectCards().length) return;
    const bar = document.querySelector(".study-edit-bar");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.setAttribute("data-flashcards", "1");
    btn.textContent = "Flashcards";
    btn.addEventListener("click", () => {
      if (overlay.hidden) openAt(0);
      else close();
    });
    if (bar) bar.appendChild(btn);
    else {
      const wrap = document.createElement("div");
      wrap.className = "study-edit-bar";
      wrap.setAttribute("data-study-flashcards", "1");
      wrap.appendChild(btn);
      document.body.appendChild(wrap);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", addButton);
  } else {
    addButton();
  }
})();
