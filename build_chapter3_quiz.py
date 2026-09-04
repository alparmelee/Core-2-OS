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
        "chapter": 3,
        "title": "Chapter 3 — Troubleshooting",
        "sections": sections,
        "terms": all_terms,
        "total": len(all_terms),
    }

    out = ROOT / "chapter3-quiz-data.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(all_terms)} terms to {out.name}")

    quiz_html = ROOT / "Chapter 3 Practice Quiz.html"
    embedded = json.dumps(data, ensure_ascii=False)
    page = quiz_page_html(
        chapter=3,
        title=data["title"],
        range_label="3.1–3.4",
        accent="#1e40af",
        accent_soft="#dbeafe",
    )
    page = page.replace(
        "study guides and interactive simulators.",
        "troubleshooting study guides.",
    )
    quiz_html.write_text(page.replace("/*__QUIZ_DATA__*/", embedded), encoding="utf-8")
    print(f"Wrote {quiz_html.name}")


if __name__ == "__main__":
    main()
