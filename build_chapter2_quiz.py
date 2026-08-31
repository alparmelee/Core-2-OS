#!/usr/bin/env python3
"""Extract terms from Chapter 2 study guides and simulators for the practice quiz."""

import json
from pathlib import Path

from build_chapter1_quiz import (
    extract_study_guide_terms,
    extract_topics_terms,
)

ROOT = Path(__file__).resolve().parent

CHAPTER2 = [
    ("2.1", "2.1 Security Measures and Their Purposes.html", "Security Measures and Their Purposes"),
    (
        "2.2",
        "2.2 Configure and Apply Basic Microsoft Windows OS Security Settings.html",
        "Windows OS Security Settings",
    ),
    ("2.3", "2.3 Wireless Security Protocols and Authentication Methods.html", "Wireless Security Protocols"),
    ("2.4", "2.4 Malware and Adware Types.html", "Malware and Adware Types"),
    (
        "2.5",
        "2.5 Social Engineering Attacks, Threats, and Vulnerabilities.html",
        "Social Engineering and Threats",
    ),
    ("2.6", "2.6 Malware Investigation and Remediation.html", "Malware Investigation and Remediation"),
    (
        "2.7",
        "2.7 Data-at-Rest Encryption and Security Best Practices.html",
        "Encryption and Security Best Practices",
    ),
    ("2.8", "2.8 Mobile Device Hardening Techniques.html", "Mobile Device Hardening"),
    ("2.9", "2.9 Data Destruction and Sanitization.html", "Data Destruction and Sanitization"),
    ("2.10", "2.10 Router, Wireless, and Firewall Settings.html", "Router and Firewall Settings"),
    ("2.11", "2.11 Browser Security and Configuration.html", "Browser Security and Configuration"),
]

TOPICS_SECTIONS = {"2.2"}


def quiz_page_html(chapter: int, title: str, range_label: str, accent: str, accent_soft: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chapter {chapter} Practice Quiz — CompTIA A+ Core 2</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,550;9..144,700&family=Sora:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{{
    --ink:#101820;
    --muted:#4b5563;
    --paper:#eef2f8;
    --line:rgba(16,24,32,0.12);
    --accent:{accent};
    --accent-soft:{accent_soft};
    --good:#166534;
    --good-soft:#dcfce7;
    --bad:#b42318;
    --bad-soft:#fee2e2;
  }}
  *{{ box-sizing:border-box; }}
  body{{
    margin:0;
    color:var(--ink);
    font-family:"Sora",sans-serif;
    background:
      radial-gradient(900px 500px at 90% -10%, color-mix(in srgb, var(--accent) 14%, transparent), transparent 55%),
      linear-gradient(180deg, #e6edf8 0%, var(--paper) 40%, #ecf1f8 100%);
    line-height:1.55;
    min-height:100vh;
  }}
  a{{ color:var(--accent); }}
  .wrap{{ width:min(760px, calc(100% - 2rem)); margin:0 auto; padding:2rem 0 3rem; }}
  .top-nav{{ margin-bottom:1.5rem; font-size:0.9rem; }}
  .top-nav a{{ text-decoration:none; font-weight:600; }}
  .top-nav a:hover{{ text-decoration:underline; }}
  h1{{
    font-family:"Fraunces",serif;
    font-size:clamp(1.8rem, 5vw, 2.6rem);
    margin:0 0 0.35rem;
    letter-spacing:-0.02em;
  }}
  .subtitle{{ color:var(--muted); margin:0 0 1.5rem; }}
  .card{{
    background:#fff;
    border:1px solid var(--line);
    border-radius:14px;
    padding:1.4rem 1.5rem;
    box-shadow:0 8px 30px rgba(16,24,32,0.06);
  }}
  .card h2{{ font-size:1rem; margin:0 0 0.75rem; }}
  .mode-row{{ display:flex; flex-direction:column; gap:0.5rem; margin:1rem 0; }}
  .mode-row label{{ display:flex; align-items:flex-start; gap:0.5rem; cursor:pointer; font-size:0.92rem; }}
  .section-grid{{
    display:grid;
    grid-template-columns:repeat(auto-fill, minmax(200px, 1fr));
    gap:0.55rem;
    margin:0.75rem 0 1rem;
  }}
  .section-card{{
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
  }}
  .section-card:hover{{
    border-color:var(--accent);
    background:var(--accent-soft);
    transform:translateY(-1px);
  }}
  .section-card-id{{ font-weight:700; color:var(--accent); font-size:0.95rem; }}
  .section-card-title{{ font-size:0.8rem; color:var(--ink); line-height:1.35; }}
  .section-card-count{{ font-size:0.72rem; color:var(--muted); }}
  .setup-focus{{ font-size:0.88rem; color:var(--muted); margin:0 0 0.75rem; }}
  .customize-block{{ margin-top:1.25rem; padding-top:1.25rem; border-top:1px solid var(--line); }}
  .toggles-grid{{ display:flex; flex-wrap:wrap; gap:0.4rem; margin:0.5rem 0 0.75rem; }}
  .check-pill{{
    display:flex;
    align-items:center;
    gap:0.4rem;
    font-size:0.82rem;
    padding:0.45rem 0.6rem;
    border:1px solid var(--line);
    border-radius:8px;
    background:#fafbfd;
    cursor:pointer;
  }}
  .check-pill em{{ color:var(--muted); font-style:normal; margin-left:auto; font-size:0.75rem; }}
  .check-pill input{{ accent-color:var(--accent); }}
  .btn{{
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
  }}
  .btn:hover{{ filter:brightness(1.05); }}
  .btn.ghost{{ background:transparent; color:var(--accent); border:1px solid var(--accent); }}
  .btn-row{{ display:flex; flex-wrap:wrap; gap:0.6rem; margin-top:1rem; }}
  .progress-wrap{{ margin-bottom:1.25rem; }}
  .progress-meta{{ display:flex; justify-content:space-between; font-size:0.82rem; color:var(--muted); margin-bottom:0.35rem; }}
  .progress-bar{{ height:8px; background:#e5e9f0; border-radius:999px; overflow:hidden; }}
  .progress-fill{{ height:100%; background:var(--accent); width:0%; transition:width .25s; }}
  .section-badge{{
    display:inline-block;
    font-size:0.72rem;
    font-weight:700;
    padding:0.2rem 0.55rem;
    border-radius:999px;
    background:var(--accent-soft);
    color:var(--accent);
    margin-bottom:0.65rem;
  }}
  .prompt-label{{ font-size:0.82rem; color:var(--muted); margin:0 0 0.35rem; }}
  .prompt-text{{
    font-family:"Fraunces",serif;
    font-size:1.35rem;
    line-height:1.35;
    margin:0 0 1.25rem;
  }}
  .choices{{ display:grid; gap:0.55rem; }}
  .choice{{
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
  }}
  .choice:hover:not(:disabled){{ border-color:var(--accent); background:var(--accent-soft); }}
  .choice:disabled{{ cursor:default; }}
  .choice.right{{ border-color:var(--good); background:var(--good-soft); }}
  .choice.wrong{{ border-color:var(--bad); background:var(--bad-soft); }}
  .feedback{{
    margin-top:1rem;
    padding:0.85rem 1rem;
    border-radius:10px;
    font-size:0.88rem;
  }}
  .feedback.good{{ background:var(--good-soft); color:var(--good); }}
  .feedback.bad{{ background:var(--bad-soft); color:var(--bad); }}
  .feedback .def-review{{ display:block; margin-top:0.35rem; color:var(--ink); }}
  .results-big{{
    font-family:"Fraunces",serif;
    font-size:3rem;
    font-weight:700;
    margin:0.25rem 0;
    letter-spacing:-0.03em;
  }}
  .review-list{{ margin-top:1.25rem; display:grid; gap:0.75rem; }}
  .review-item{{
    border:1px solid var(--line);
    border-radius:10px;
    padding:0.85rem 1rem;
    background:#fafbfd;
    font-size:0.88rem;
  }}
  .review-item strong{{ display:block; margin-bottom:0.25rem; }}
  .review-item p{{ margin:0; color:var(--muted); }}
  .review-meta{{ font-size:0.72rem; font-weight:700; color:var(--accent); margin-bottom:0.2rem; }}
  .all-good{{ color:var(--good); font-weight:600; }}
  [hidden]{{ display:none !important; }}
</style>
</head>
<body>
  <div class="wrap">
    <nav class="top-nav"><a href="index.html">← All guides</a></nav>

    <div data-screen="setup">
      <h1>Chapter {chapter} Practice Quiz</h1>
      <p class="subtitle"><span id="term-count">0</span> terms from objectives {range_label} — study guides and interactive simulators.</p>
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
      <h1 id="quiz-heading">Chapter {chapter} Quiz</h1>
      <div class="progress-wrap">
        <div class="progress-meta">
          <span id="progress-label">Question 1 of 10</span>
          <span id="score-live">0 correct</span>
        </div>
        <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
      </div>
      <div class="card">
        <div class="section-badge" id="section-badge">2.1</div>
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


def main():
    all_terms = []
    sections = []

    for section_id, filename, title in CHAPTER2:
        path = ROOT / filename
        html = path.read_text(encoding="utf-8")
        if section_id in TOPICS_SECTIONS:
            terms = extract_topics_terms(html)
        else:
            terms = extract_study_guide_terms(html)

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
        "chapter": 2,
        "title": "Chapter 2 — Security",
        "sections": sections,
        "terms": all_terms,
        "total": len(all_terms),
    }

    out = ROOT / "chapter2-quiz-data.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(all_terms)} terms to {out.name}")

    quiz_html = ROOT / "Chapter 2 Practice Quiz.html"
    embedded = json.dumps(data, ensure_ascii=False)
    page = quiz_page_html(
        chapter=2,
        title=data["title"],
        range_label="2.1–2.11",
        accent="#9a3412",
        accent_soft="#ffedd5",
    )
    quiz_html.write_text(page.replace("/*__QUIZ_DATA__*/", embedded), encoding="utf-8")
    print(f"Wrote {quiz_html.name}")


if __name__ == "__main__":
    main()
