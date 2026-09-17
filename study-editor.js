/**
 * In-page term editor for personal study guides.
 * Requires the local save server: python study-save-server.py
 * Then open pages via http://localhost:8765/...
 */
(function () {
  "use strict";

  const PORT = 8765;
  const SAVE_URL = "http://127.0.0.1:" + PORT + "/__save__";
  const PING_URL = "http://127.0.0.1:" + PORT + "/__ping__";

  let editing = false;
  let serverOk = false;

  const style = document.createElement("style");
  style.textContent = `
    .study-edit-bar{
      position:fixed; right:1rem; bottom:1rem; z-index:1200;
      display:flex; flex-wrap:wrap; gap:0.45rem; align-items:center;
      padding:0.55rem 0.65rem; border-radius:14px;
      background:rgba(16,24,32,0.92); color:#f8fafc;
      box-shadow:0 12px 32px rgba(0,0,0,0.28);
      font:600 0.82rem/1 Sora, system-ui, sans-serif;
    }
    .study-edit-bar button{
      font:inherit; cursor:pointer; border:0; border-radius:999px;
      padding:0.5rem 0.85rem; background:#e2e8f0; color:#0f172a;
    }
    .study-edit-bar button.primary{ background:#34d399; color:#064e3b; }
    .study-edit-bar button:disabled{ opacity:0.45; cursor:default; }
    .study-edit-bar .status{ font-weight:500; color:#cbd5e1; max-width:16rem; }
    .study-edit-bar .status.ok{ color:#86efac; }
    .study-edit-bar .status.err{ color:#fda4af; }
    .term .body[contenteditable="true"]{
      outline:2px dashed rgba(15,110,86,0.45);
      outline-offset:6px; border-radius:8px; padding:0.25rem;
      min-height:2.5rem;
    }
    .term .body[contenteditable="true"]:focus{
      outline-color:rgba(15,110,86,0.85);
      background:rgba(255,255,255,0.35);
    }
    .study-add-p{
      margin-top:0.55rem; font:600 0.78rem Sora, system-ui, sans-serif;
      border:1px dashed rgba(15,110,86,0.45); background:rgba(15,110,86,0.08);
      color:#0f6e56; border-radius:999px; padding:0.35rem 0.75rem; cursor:pointer;
    }
    .study-add-p[hidden]{ display:none; }
  `;
  document.head.appendChild(style);

  const bar = document.createElement("div");
  bar.className = "study-edit-bar";
  bar.setAttribute("data-study-editor", "1");
  bar.innerHTML =
    '<span class="status" data-status>Checking save server…</span>' +
    '<button type="button" data-edit>Edit terms</button>' +
    '<button type="button" class="primary" data-save disabled>Save</button>';
  document.body.appendChild(bar);

  const statusEl = bar.querySelector("[data-status]");
  const editBtn = bar.querySelector("[data-edit]");
  const saveBtn = bar.querySelector("[data-save]");

  function setStatus(msg, kind) {
    statusEl.textContent = msg;
    statusEl.className = "status" + (kind ? " " + kind : "");
  }

  function pagePath() {
    let path = decodeURIComponent(location.pathname || "");
    if (path.startsWith("/")) path = path.slice(1);
    return path;
  }

  async function ping() {
    try {
      const res = await fetch(PING_URL, { cache: "no-store" });
      serverOk = res.ok;
    } catch (_) {
      serverOk = false;
    }
    if (serverOk) {
      setStatus("Ready — edit, then Save", "ok");
      saveBtn.disabled = !editing;
    } else {
      setStatus("Start server: python study-save-server.py", "err");
      saveBtn.disabled = true;
    }
  }

  function bodies() {
    return Array.from(document.querySelectorAll("article.term .body"));
  }

  function setEditing(on) {
    editing = on;
    bodies().forEach((el) => {
      el.contentEditable = on ? "true" : "false";
      let add = el.querySelector(".study-add-p");
      if (on) {
        if (!add) {
          add = document.createElement("button");
          add.type = "button";
          add.className = "study-add-p";
          add.textContent = "+ Add text";
          add.addEventListener("click", (e) => {
            e.preventDefault();
            const p = document.createElement("p");
            p.textContent = "New note…";
            el.insertBefore(p, add);
            p.focus();
            const range = document.createRange();
            range.selectNodeContents(p);
            const sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
          });
          el.appendChild(add);
        }
        add.hidden = false;
      } else if (add) {
        add.hidden = true;
      }
    });
    editBtn.textContent = on ? "Done editing" : "Edit terms";
    saveBtn.disabled = !(on && serverOk);
    if (on && serverOk) setStatus("Editing — click Save when finished", "ok");
    else if (!on && serverOk) setStatus("Ready — edit, then Save", "ok");
  }

  function cleanCloneForSave() {
    const clone = document.documentElement.cloneNode(true);
    clone.querySelectorAll("[data-study-editor]").forEach((n) => n.remove());
    clone.querySelectorAll("[data-study-flashcards]").forEach((n) => n.remove());
    clone.querySelectorAll(".study-fc-overlay").forEach((n) => n.remove());
    clone.querySelectorAll(".study-add-p").forEach((n) => n.remove());
    clone.querySelectorAll(".study-lightbox").forEach((n) => n.remove());
    clone.querySelectorAll("[contenteditable]").forEach((n) => {
      n.removeAttribute("contenteditable");
    });
    clone.querySelectorAll("style").forEach((st) => {
      if ((st.textContent || "").includes(".study-edit-bar")) st.remove();
      if ((st.textContent || "").includes(".study-fc-overlay")) st.remove();
    });
    // Keep a single study-editor script tag if present; drop duplicates
    const editors = clone.querySelectorAll('script[src="study-editor.js"]');
    editors.forEach((s, i) => {
      if (i > 0) s.remove();
    });
    return "<!DOCTYPE html>\n" + clone.outerHTML + "\n";
  }

  async function save() {
    if (!serverOk) {
      setStatus("Save server not running", "err");
      return;
    }
    saveBtn.disabled = true;
    setStatus("Saving…");
    try {
      const res = await fetch(SAVE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path: pagePath(),
          html: cleanCloneForSave(),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Save failed");
      setStatus("Saved to " + (data.path || "file"), "ok");
    } catch (err) {
      setStatus(err.message || "Save failed", "err");
      await ping();
    } finally {
      saveBtn.disabled = !(editing && serverOk);
    }
  }

  editBtn.addEventListener("click", () => setEditing(!editing));
  saveBtn.addEventListener("click", save);

  ping();
  setInterval(ping, 8000);

  const fc = document.createElement("script");
  fc.src = "study-flashcards.js";
  document.body.appendChild(fc);
})();
