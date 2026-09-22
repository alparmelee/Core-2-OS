#!/usr/bin/env python3
"""Extract terms from Chapter 4 study guides for the practice quiz."""

import json
from pathlib import Path

from build_chapter1_quiz import extract_study_guide_terms
from build_chapter2_quiz import quiz_page_html

ROOT = Path(__file__).resolve().parent

CHAPTER4 = [
    (
        "4.1",
        "4.1 Documentation and Support Systems Information Management.html",
        "Documentation and Support Systems",
    ),
    (
        "4.2",
        "4.2 Change Management Best Practices.html",
        "Change Management Best Practices",
    ),
    (
        "4.3",
        "4.3 Backup and Recovery Best Practices.html",
        "Backup and Recovery Best Practices",
    ),
    (
        "4.4",
        "4.4 Safety and Environmental Controls.html",
        "Safety and Environmental Controls",
    ),
    (
        "4.5",
        "4.5 MSDS, Disposal, and Power Protection.html",
        "MSDS, Disposal, and Power Protection",
    ),
    (
        "4.6",
        "4.6 Incident Response, Licensing, and Compliance.html",
        "Incident Response, Licensing, and Compliance",
    ),
    (
        "4.7",
        "4.7 Professionalism and Customer Service.html",
        "Professionalism and Customer Service",
    ),
    (
        "4.8",
        "4.8 Scripting Basics and Use Cases.html",
        "Scripting Basics and Use Cases",
    ),
    (
        "4.9",
        "4.9 Remote Access Tools and Security.html",
        "Remote Access Tools and Security",
    ),
    (
        "4.10",
        "4.10 AI Tools, Policy, and Limitations.html",
        "AI Tools, Policy, and Limitations",
    ),
]


def main():
    all_terms = []
    sections = []
    existing_scenarios = {}
    prev_path = ROOT / "chapter4-quiz-data.json"
    if prev_path.exists():
        prev = json.loads(prev_path.read_text(encoding="utf-8"))
        for t in prev.get("terms", []):
            if t.get("scenario"):
                existing_scenarios[t["id"]] = t["scenario"]
                existing_scenarios[(t.get("section"), t.get("name"))] = t["scenario"]

    for section_id, filename, title in CHAPTER4:
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
        "chapter": 4,
        "title": "Chapter 4 — Operational Procedures",
        "sections": sections,
        "terms": all_terms,
        "total": len(all_terms),
    }

    out = ROOT / "chapter4-quiz-data.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(all_terms)} terms to {out.name}")

    js_out = ROOT / "chapter4-quiz-data.js"
    js_out.write_text(
        "window.QUIZ_DATA = " + json.dumps(data, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {js_out.name}")

    quiz_html = ROOT / "Chapter 4 Practice Quiz.html"
    page = quiz_page_html(
        chapter=4,
        title=data["title"],
        range_label="4.1–4.10",
        accent="#0d9488",
        accent_soft="#ccfbf1",
        data_js="chapter4-quiz-data.js",
    )
    quiz_html.write_text(page, encoding="utf-8")
    print(f"Wrote {quiz_html.name}")


if __name__ == "__main__":
    main()
