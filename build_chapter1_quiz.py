#!/usr/bin/env python3
"""Extract terms from Chapter 1 study guides and simulators for the practice quiz."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CHAPTER1 = [
    ("1.1", "1.1 Operating Systems and File Systems.html", "Operating Systems and File Systems"),
    ("1.2", "1.2 OS Installation and Boot Methods.html", "OS Installation and Boot Methods"),
    ("1.3", "1.3 Microsoft Windows Editions.html", "Microsoft Windows Editions"),
    ("1.4", "1.4 Microsoft Windows Operating System Features and Tools.html", "Windows Features and Tools"),
    ("1.5", "1.5 Microsoft Command-Line Tools.html", "Command-Line Tools"),
    ("1.6", "1.6 Configure Microsoft Windows Settings.html", "Configure Windows Settings"),
    ("1.7", "1.7 Configure Microsoft Windows Networking.html", "Windows Networking"),
    ("1.8", "1.8 Common Features and Tools of the macOS Desktop Operating System.html", "macOS Features and Tools"),
    ("1.9", "1.9 Linux Features and Tools.html", "Linux Features and Tools"),
    ("1.10", "1.10 Installing Applications.html", "Installing Applications"),
    ("1.11", "1.11 Configure Cloud-Based Productivity Tools.html", "Cloud Productivity Tools"),
]


class TermParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.terms = []
        self._in_term = False
        self._in_body = False
        self._in_h3 = False
        self._in_p = False
        self._in_li = False
        self._current = None
        self._buf = []
        self._list_parts = []

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if tag == "article" and "term" in cls.split():
            self._in_term = True
            self._current = {"name": "", "definition": ""}
            self._list_parts = []
        elif self._in_term and tag == "div" and "body" in cls.split():
            self._in_body = True
        elif self._in_body and tag == "h3":
            self._in_h3 = True
            self._buf = []
        elif self._in_body and tag == "p" and self._current and not self._current["definition"]:
            self._in_p = True
            self._buf = []
        elif self._in_body and tag == "li":
            self._in_li = True
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "article" and self._in_term:
            if self._current and self._current["name"]:
                if not self._current["definition"] and self._list_parts:
                    self._current["definition"] = " ".join(self._list_parts)
                if self._current["definition"]:
                    self.terms.append(self._current)
            self._in_term = False
            self._in_body = False
            self._current = None
            self._list_parts = []
        elif tag == "div" and self._in_body:
            self._in_body = False
        elif tag == "h3" and self._in_h3:
            self._in_h3 = False
            if self._current:
                self._current["name"] = "".join(self._buf).strip()
        elif tag == "p" and self._in_p:
            self._in_p = False
            if self._current and not self._current["definition"]:
                self._current["definition"] = " ".join("".join(self._buf).split())
        elif tag == "li" and self._in_li:
            self._in_li = False
            text = " ".join("".join(self._buf).split())
            if text:
                self._list_parts.append(text)

    def handle_data(self, data):
        if self._in_h3 or self._in_p or self._in_li:
            self._buf.append(data)


def extract_study_guide_terms(html: str) -> list[dict]:
    parser = TermParser()
    parser.feed(html)
    return parser.terms


def unescape_js(s: str) -> str:
    return (
        s.replace("\\'", "'")
        .replace('\\"', '"')
        .replace("\\n", " ")
        .replace("\\u2019", "'")
        .replace("\\u2014", "—")
        .replace("\\u2013", "–")
        .replace("\\u2026", "…")
    )


def extract_field(text: str, field: str) -> str | None:
    m = re.search(
        rf"{field}\s*:\s*(?:'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\"|`((?:\\`|[^`])*)`)",
        text,
    )
    if not m:
        return None
    return unescape_js(next(g for g in m.groups() if g is not None)).strip()


def extract_apps_terms(html: str) -> list[dict]:
    """Extract Windows admin tool entries from APPS array (multiline objects)."""
    terms = []
    pattern = re.compile(
        r"\{\s*id:'[^']+',\s*name:'([^']+)',\s*emoji:[^,]+,\s*color:\d+,\s*cmd:'[^']*',\s*"
        r"short:'((?:\\'|[^'])*)',\s*long:'((?:\\'|[^'])*)'",
        re.DOTALL,
    )
    for m in pattern.finditer(html):
        name, short, long = m.group(1), unescape_js(m.group(2)), unescape_js(m.group(3))
        definition = short
        if long and long != short:
            definition = f"{short} {long}"
        terms.append({"name": name, "definition": definition.strip()})
    return terms


def extract_reference_lines(html: str) -> list[dict]:
    """Extract reference panel items (one object per line)."""
    terms = []
    in_block = False
    for line in html.splitlines():
        if "const reference = [" in line:
            in_block = True
            continue
        if in_block:
            if line.strip() == "];":
                break
            if "name:" not in line:
                continue
            name = extract_field(line, "name")
            if not name:
                continue
            parts = []
            for field in ("desc", "short", "long", "example", "path", "action"):
                val = extract_field(line, field)
                if val:
                    parts.append(val)
            definition = " ".join(parts).strip()
            if definition:
                terms.append({"name": name, "definition": definition})
    return terms


def extract_js_array_block(text: str, var_name: str) -> str:
    marker = f"const {var_name} = ["
    start = text.find(marker)
    if start == -1:
        return ""
    i = start + len(marker) - 1
    depth = 0
    in_str = None
    escape = False
    while i < len(text):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_str:
                in_str = None
        else:
            if ch in ("'", '"', "`"):
                in_str = ch
            elif ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return text[start + len(marker) : i]
        i += 1
    return ""


def extract_topics_terms(html: str) -> list[dict]:
    """Extract 1.10 topics array entries."""
    block = extract_js_array_block(html, "topics")
    if not block:
        return []
    terms = []
    chunks = re.split(r"(?=\{\s*id:')", block)
    for chunk in chunks:
        if "id:'" not in chunk:
            continue
        name = extract_field(chunk, "name")
        desc = extract_field(chunk, "desc")
        group = extract_field(chunk, "group")
        if name and desc:
            definition = f"{group}: {desc}" if group else desc
            terms.append({"name": name, "definition": definition})
    return terms


def extract_simulator_terms(html: str, section_id: str) -> list[dict]:
    terms = []
    seen = set()

    def add(term: dict):
        name = term["name"].strip()
        if not name or name in seen:
            return
        definition = term["definition"].strip()
        if not definition:
            return
        seen.add(name)
        terms.append({"name": name, "definition": definition})

    if section_id == "1.4":
        for t in extract_apps_terms(html):
            add(t)
    elif section_id == "1.10":
        for t in extract_topics_terms(html):
            add(t)
    else:
        for t in extract_reference_lines(html):
            add(t)

    return terms


def main():
    all_terms = []
    sections = []

    for section_id, filename, title in CHAPTER1:
        path = ROOT / filename
        html = path.read_text(encoding="utf-8")
        if section_id in ("1.1", "1.2", "1.3"):
            terms = extract_study_guide_terms(html)
        else:
            terms = extract_simulator_terms(html, section_id)

        section_terms = []
        for t in terms:
            entry = {
                "id": f"{section_id}-{len(section_terms)}",
                "section": section_id,
                "sectionTitle": title,
                "name": t["name"],
                "definition": t["definition"],
            }
            section_terms.append(entry)
            all_terms.append(entry)

        sections.append(
            {
                "id": section_id,
                "title": title,
                "file": filename,
                "count": len(section_terms),
            }
        )
        print(f"{section_id}: {len(section_terms)} terms")

    data = {
        "chapter": 1,
        "title": "Chapter 1 — Operating Systems",
        "sections": sections,
        "terms": all_terms,
        "total": len(all_terms),
    }

    out = ROOT / "chapter1-quiz-data.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(all_terms)} terms to {out.name}")

    quiz_html = ROOT / "Chapter 1 Practice Quiz.html"
    embedded = json.dumps(data, ensure_ascii=False)
    quiz_html.write_text(QUIZ_PAGE_HTML.replace("/*__QUIZ_DATA__*/", embedded), encoding="utf-8")
    print(f"Wrote {quiz_html.name}")


QUIZ_PAGE_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chapter 1 Practice Quiz — CompTIA A+ Core 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,550;9..144,700&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --ink:#101820;
    --muted:#4b5563;
    --paper:#eef2f8;
    --line:rgba(16,24,32,0.12);
    --accent:#1d4ed8;
    --accent-soft:#dbeafe;
    --good:#166534;
    --good-soft:#dcfce7;
    --bad:#b42318;
    --bad-soft:#fee2e2;
  }
  *{ box-sizing:border-box; }
  body{
    margin:0;
    color:var(--ink);
    font-family:"Sora",sans-serif;
    background:
      radial-gradient(900px 500px at 90% -10%, rgba(29,78,216,0.12), transparent 55%),
      linear-gradient(180deg, #e6edf8 0%, var(--paper) 40%, #ecf1f8 100%);
    line-height:1.55;
    min-height:100vh;
  }
  a{ color:var(--accent); }
  .wrap{ width:min(760px, calc(100% - 2rem)); margin:0 auto; padding:2rem 0 3rem; }
  .top-nav{ margin-bottom:1.5rem; font-size:0.9rem; }
  .top-nav a{ text-decoration:none; font-weight:600; }
  .top-nav a:hover{ text-decoration:underline; }
  h1{
    font-family:"Fraunces",serif;
    font-size:clamp(1.8rem, 5vw, 2.6rem);
    margin:0 0 0.35rem;
    letter-spacing:-0.02em;
  }
  .subtitle{ color:var(--muted); margin:0 0 1.5rem; }
  .card{
    background:#fff;
    border:1px solid var(--line);
    border-radius:14px;
    padding:1.4rem 1.5rem;
    box-shadow:0 8px 30px rgba(16,24,32,0.06);
  }
  .card h2{ font-size:1rem; margin:0 0 0.75rem; }
  .mode-row{ display:flex; flex-direction:column; gap:0.5rem; margin:1rem 0; }
  .mode-row label{ display:flex; align-items:flex-start; gap:0.5rem; cursor:pointer; font-size:0.92rem; }
  .section-grid{
    display:grid;
    grid-template-columns:repeat(auto-fill, minmax(200px, 1fr));
    gap:0.55rem;
    margin:0.75rem 0 1rem;
  }
  .section-card{
    text-align:left;
    border:1px solid var(--line);
    background:#fafbfd;
    border-radius:12px;
    padding:0.85rem 1rem;
    cursor:pointer;
    display:flex;
    flex-direction:column;
    gap:0.2rem;
    font-family:inherit;
    transition:border-color .15s, background .15s, transform .15s;
  }
  .section-card:hover{
    border-color:var(--accent);
    background:var(--accent-soft);
    transform:translateY(-1px);
  }
  .section-card-id{ font-weight:700; color:var(--accent); font-size:0.95rem; }
  .section-card-title{ font-size:0.8rem; color:var(--ink); line-height:1.35; }
  .section-card-count{ font-size:0.72rem; color:var(--muted); }
  .setup-focus{ font-size:0.88rem; color:var(--muted); margin:0 0 0.75rem; }
  .customize-block{ margin-top:1.25rem; padding-top:1.25rem; border-top:1px solid var(--line); }
  .toggles-grid{ display:flex; flex-wrap:wrap; gap:0.4rem; margin:0.5rem 0 0.75rem; }
  .check-pill{
    display:flex;
    align-items:center;
    gap:0.4rem;
    font-size:0.82rem;
    padding:0.45rem 0.6rem;
    border:1px solid var(--line);
    border-radius:8px;
    background:#fafbfd;
    cursor:pointer;
  }
  .check-pill em{ color:var(--muted); font-style:normal; margin-left:auto; font-size:0.75rem; }
  .check-pill input{ accent-color:var(--accent); }
  .btn{
    appearance:none;
    border:none;
    border-radius:999px;
    padding:0.75rem 1.4rem;
    font-family:inherit;
    font-weight:600;
    font-size:0.92rem;
    cursor:pointer;
    background:var(--accent);
    color:#fff;
  }
  .btn:hover{ filter:brightness(1.05); }
  .btn.ghost{ background:transparent; color:var(--accent); border:1px solid var(--accent); }
  .btn-row{ display:flex; flex-wrap:wrap; gap:0.6rem; margin-top:1rem; }
  .progress-wrap{ margin-bottom:1.25rem; }
  .progress-meta{ display:flex; justify-content:space-between; font-size:0.82rem; color:var(--muted); margin-bottom:0.35rem; }
  .progress-bar{ height:8px; background:#e5e9f0; border-radius:999px; overflow:hidden; }
  .progress-fill{ height:100%; background:var(--accent); width:0%; transition:width .25s; }
  .section-badge{
    display:inline-block;
    font-size:0.72rem;
    font-weight:700;
    padding:0.2rem 0.55rem;
    border-radius:999px;
    background:var(--accent-soft);
    color:var(--accent);
    margin-bottom:0.65rem;
  }
  .prompt-label{ font-size:0.82rem; color:var(--muted); margin:0 0 0.35rem; }
  .prompt-text{
    font-family:"Fraunces",serif;
    font-size:1.35rem;
    line-height:1.35;
    margin:0 0 1.25rem;
  }
  .choices{ display:grid; gap:0.55rem; }
  .choice{
    text-align:left;
    border:1px solid var(--line);
    background:#fafbfd;
    border-radius:10px;
    padding:0.85rem 1rem;
    font-family:inherit;
    font-size:0.88rem;
    line-height:1.45;
    cursor:pointer;
    transition:background .15s, border-color .15s;
  }
  .choice:hover:not(:disabled){ border-color:var(--accent); background:var(--accent-soft); }
  .choice:disabled{ cursor:default; }
  .choice.right{ border-color:var(--good); background:var(--good-soft); }
  .choice.wrong{ border-color:var(--bad); background:var(--bad-soft); }
  .feedback{
    margin-top:1rem;
    padding:0.85rem 1rem;
    border-radius:10px;
    font-size:0.88rem;
  }
  .feedback.good{ background:var(--good-soft); color:var(--good); }
  .feedback.bad{ background:var(--bad-soft); color:var(--bad); }
  .feedback .def-review{ display:block; margin-top:0.35rem; color:var(--ink); }
  .results-big{
    font-family:"Fraunces",serif;
    font-size:3rem;
    font-weight:700;
    margin:0.25rem 0;
    letter-spacing:-0.03em;
  }
  .review-list{ margin-top:1.25rem; display:grid; gap:0.75rem; }
  .review-item{
    border:1px solid var(--line);
    border-radius:10px;
    padding:0.85rem 1rem;
    background:#fafbfd;
    font-size:0.88rem;
  }
  .review-item strong{ display:block; margin-bottom:0.25rem; }
  .review-item p{ margin:0; color:var(--muted); }
  .review-meta{ font-size:0.72rem; font-weight:700; color:var(--accent); margin-bottom:0.2rem; }
  .all-good{ color:var(--good); font-weight:600; }
  [hidden]{ display:none !important; }
</style>
</head>
<body>
  <div class="wrap">
    <nav class="top-nav"><a href="index.html">← All guides</a></nav>

    <div data-screen="setup">
      <h1>Chapter 1 Practice Quiz</h1>
      <p class="subtitle"><span id="term-count">0</span> terms from objectives 1.1–1.11 — study guides and interactive simulators.</p>
      <div class="card">
        <h2>Quiz mode</h2>
        <div class="mode-row">
          <label><input type="radio" name="quiz-mode" value="term-to-def" checked> Term → pick the correct definition</label>
          <label><input type="radio" name="quiz-mode" value="def-to-term"> Definition → pick the correct term</label>
        </div>
        <p class="setup-focus" id="setup-focus">Click a section to start instantly.</p>
        <h2>Start a section</h2>
        <div class="section-grid" id="section-filters"></div>
        <button type="button" class="btn" id="start-all-btn">Quiz all sections</button>
        <div class="customize-block">
          <h2>Or combine sections</h2>
          <div class="toggles-grid" id="section-toggles"></div>
          <button type="button" class="btn ghost" id="start-btn">Start custom quiz</button>
        </div>
      </div>
    </div>

    <div data-screen="quiz" hidden>
      <h1>Chapter 1 Quiz</h1>
      <div class="progress-wrap">
        <div class="progress-meta">
          <span id="progress-label">Question 1 of 10</span>
          <span id="score-live">0 correct</span>
        </div>
        <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
      </div>
      <div class="card">
        <div class="section-badge" id="section-badge">1.1</div>
        <p class="prompt-label" id="prompt-label">Which definition best describes this term?</p>
        <p class="prompt-text" id="prompt-text">—</p>
        <div class="choices" id="choices"></div>
        <div class="feedback" id="feedback" hidden></div>
        <div class="btn-row">
          <button type="button" class="btn" id="next-btn" hidden>Next question</button>
        </div>
      </div>
    </div>

    <div data-screen="results" hidden>
      <h1>Results</h1>
      <div class="card">
        <p class="subtitle" style="margin:0;">Your score</p>
        <div class="results-big" id="results-score">0 / 0</div>
        <p id="results-pct" style="margin:0; color:var(--muted);">0%</p>
        <div class="btn-row">
          <button type="button" class="btn" id="retry-btn">Retry missed terms</button>
          <button type="button" class="btn ghost" id="restart-btn">New quiz</button>
        </div>
        <div class="review-list" id="review-list"></div>
      </div>
    </div>
  </div>

  <script>window.QUIZ_DATA = /*__QUIZ_DATA__*/;</script>
  <script src="study-quiz.js"></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
