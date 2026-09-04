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
        "chapter": 4,
        "title": "Chapter 4 — Operational Procedures",
        "sections": sections,
        "terms": all_terms,
        "total": len(all_terms),
    }

    out = ROOT / "chapter4-quiz-data.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(all_terms)} terms to {out.name}")

    quiz_html = ROOT / "Chapter 4 Practice Quiz.html"
    embedded = json.dumps(data, ensure_ascii=False)
    page = quiz_page_html(
        chapter=4,
        title=data["title"],
        range_label="4.1–4.10",
        accent="#0d9488",
        accent_soft="#ccfbf1",
    )
    page = page.replace(
        "study guides and interactive simulators.",
        "operational procedures study guides.",
    )
    quiz_html.write_text(page.replace("/*__QUIZ_DATA__*/", embedded), encoding="utf-8")
    print(f"Wrote {quiz_html.name}")


if __name__ == "__main__":
    main()
