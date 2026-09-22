#!/usr/bin/env python3
"""Extract terms from Chapter 3 study guides for the practice quiz."""

import json
from pathlib import Path

from build_chapter1_quiz import extract_study_guide_terms
from build_chapter2_quiz import quiz_page_html

ROOT = Path(__file__).resolve().parent

CHAPTER3 = [
    (
        "3.1",
        "3.1 Troubleshoot Microsoft Windows OS Problems.html",
        "Troubleshoot Microsoft Windows OS Problems",
    ),
    (
        "3.2",
        "3.2 Troubleshoot Mobile OS and Application Issues.html",
        "Troubleshoot Mobile OS and Application Issues",
    ),
    (
        "3.3",
        "3.3 Troubleshoot Mobile OS and Application Security Issues.html",
        "Troubleshoot Mobile OS and Application Security Issues",
    ),
    (
        "3.4",
        "3.4 Troubleshoot Windows OS Security Issues.html",
        "Troubleshoot Windows OS Security Issues",
    ),
]


def main():
    all_terms = []
    sections = []
    existing_scenarios = {}
    prev_path = ROOT / "chapter3-quiz-data.json"
    if prev_path.exists():
        prev = json.loads(prev_path.read_text(encoding="utf-8"))
        for t in prev.get("terms", []):
            if t.get("scenario"):
                existing_scenarios[t["id"]] = t["scenario"]
                existing_scenarios[(t.get("section"), t.get("name"))] = t["scenario"]

    for section_id, filename, title in CHAPTER3:
        path = ROOT / filename
        html = path.read_text(encoding="utf-8")
        terms = extract_study_guide_terms(html)

        section_terms = []
        for t in terms:
            entry = {
                "id": f"{section_id}-{len(section_terms)}",
                "section": section_id,
                "sectionTitle": title,
                "category": t.get("category", ""),
                "name": t["name"],
                "definition": t["definition"],
            }
            prev = existing_scenarios.get(entry["id"]) or existing_scenarios.get(
                (section_id, t["name"])
            )
            if prev:
                entry["scenario"] = prev
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
        "chapter": 3,
        "title": "Chapter 3 — Troubleshooting",
        "sections": sections,
        "terms": all_terms,
        "total": len(all_terms),
    }

    out = ROOT / "chapter3-quiz-data.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(all_terms)} terms to {out.name}")

    js_out = ROOT / "chapter3-quiz-data.js"
    js_out.write_text(
        "window.QUIZ_DATA = " + json.dumps(data, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {js_out.name}")

    quiz_html = ROOT / "Chapter 3 Practice Quiz.html"
    page = quiz_page_html(
        chapter=3,
        title=data["title"],
        range_label="3.1–3.4",
        accent="#1e40af",
        accent_soft="#dbeafe",
        data_js="chapter3-quiz-data.js",
    )
    quiz_html.write_text(page, encoding="utf-8")
    print(f"Wrote {quiz_html.name}")


if __name__ == "__main__":
    main()
