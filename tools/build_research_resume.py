#!/usr/bin/env python3
"""Build a two-page Research Scientist resume and its matching web page.

Tailored narrative lives in _data/research_resume.yml. Names, appointments,
education, bibliography, and contact details are resolved from the academic CV
and canonical site configuration. --check rejects missing or stale outputs.
"""

import argparse
from datetime import date
from functools import partial
from hashlib import sha256
from html import escape
from io import BytesIO
import json
from pathlib import Path
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer
import yaml

import build_academic_cv as academic


ROOT = Path(__file__).resolve().parents[1]
WEB_PATH = Path("_pages/cv-research.md")
PDF_PATH = Path("assets/cv-research-scientist.pdf")
LEGACY_PDFS = tuple(Path(f"assets/cv-{role}.pdf") for role in ("fde", "robotics", "ml", "applied-ai", "solutions-engineer"))
REBUILD = "python tools/build_research_resume.py"
SUBJECT = "Research Scientist resume source SHA256: "
NAVY, TEAL, GRAY = academic.NAVY, academic.TEAL, academic.GRAY


def nonempty_list(value, label):
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a nonempty list")
    return value


def section_items(cv, title):
    matches = [section for section in cv["sections"] if section["title"] == title]
    if len(matches) != 1 or "items" not in matches[0]:
        raise ValueError(f"Canonical CV must contain exactly one {title!r} items section")
    return matches[0]["items"]


def resolve(items, field, reference, label):
    reference = academic.string(reference, label, required=True)
    matches = [item for item in items if item[field] == reference]
    if len(matches) != 1:
        raise ValueError(f"{label} must match exactly one canonical {field}; found {len(matches)} for {reference!r}")
    return dict(matches[0])


def selected_entries(source, field, entries, reference_key, canonical_field):
    result, seen = [], set()
    for index, raw in enumerate(nonempty_list(source.get(field), f"research_resume.{field}")):
        label = f"research_resume.{field}[{index}]"
        raw = academic.mapping(raw, label)
        reference = academic.string(raw.get(reference_key), f"{label}.{reference_key}", required=True)
        if reference in seen:
            raise ValueError(f"{label} duplicates the reference {reference!r}")
        seen.add(reference)
        item = resolve(entries, canonical_field, reference, f"{label}.{reference_key}")
        # Only the narrative can be tailored; appointment names and dates remain canonical.
        item["text"], item["links"] = "", {}
        item["bullets"] = [academic.string(bullet, f"{label}.bullets", required=True)
                           for bullet in nonempty_list(raw.get("bullets"), f"{label}.bullets")]
        if field == "research" and "title" in raw:
            item["title"] = academic.string(raw["title"], f"{label}.title", required=True)
        result.append(item)
    return result


def load_sources(root):
    canonical = academic.load_sources(root)
    source = academic.load_yaml(root / "_data/research_resume.yml")
    updated = source.get("updated")
    if isinstance(updated, date):
        updated = updated.isoformat()
    updated = academic.string(updated, "research_resume.updated", required=True)
    if date.fromisoformat(updated).isoformat() != updated:
        raise ValueError("research_resume.updated must have YYYY-MM-DD format")
    resume = {key: canonical[key] for key in ("name", "credentials", "location", "contacts")}
    resume.update(updated=updated,
                  headline=academic.string(source.get("headline"), "research_resume.headline", required=True),
                  summary=academic.string(source.get("summary"), "research_resume.summary", required=True),
                  source_url=canonical["source_url"] + "research/")
    resume["experience"] = selected_entries(source, "experience",
                                            section_items(canonical, "Academic and Research Appointments"),
                                            "appointment", "subtitle")
    resume["research"] = selected_entries(source, "research",
                                          section_items(canonical, "Research and Engineering Projects"),
                                          "project", "title")
    resume["education"] = []
    seen = set()
    for reference in nonempty_list(source.get("education"), "research_resume.education"):
        item = resolve(section_items(canonical, "Education"), "subtitle", reference, "research_resume.education")
        if item["subtitle"] in seen:
            raise ValueError("research_resume.education contains a duplicate reference")
        seen.add(item["subtitle"])
        resume["education"].append(item)
    publications = [item for section in canonical["sections"] for group in section.get("groups", []) for item in group["items"]]
    resume["publications"], seen = [], set()
    for reference in nonempty_list(source.get("publications"), "research_resume.publications"):
        item = resolve(publications, "title", reference, "research_resume.publications")
        if item["title"] in seen:
            raise ValueError("research_resume.publications contains a duplicate reference")
        seen.add(item["title"])
        resume["publications"].append(item)
    resume["skills"] = []
    for raw in nonempty_list(source.get("skills"), "research_resume.skills"):
        raw = academic.mapping(raw, "research_resume.skills entry")
        resume["skills"].append({key: academic.string(raw.get(key), f"research_resume.skills.{key}", required=True)
                                  for key in ("title", "text")})
    return resume


def source_fingerprint(root, resume):
    digest = sha256(json.dumps(resume, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    for relative in ("tools/build_research_resume.py", "tools/build_academic_cv.py",
                     "tools/requirements-academic-cv.txt", "tools/requirements-contact.txt"):
        digest.update(b"\0" + relative.encode("ascii") + b"\0" + (root / relative).read_bytes())
    return digest.hexdigest()


def publication_html(item, pdf=False):
    esc = academic.pdf_escape if pdf else escape
    linker = academic.pdf_link if pdf else academic.link_html
    # Publication status is explicit, especially when a selection is a preprint.
    kind = {"journal": "Journal article", "conference": "Conference paper", "preprint": "Preprint"}.get(item["type"], item["type"].title())
    parts = [f'<b>{esc(item["title"].rstrip("."))}.</b>', esc(item["authors"]) + ".",
             f'<i>{esc(item["venue"].rstrip("."))}</i>, {item["year"]}.', f'[{esc(kind)}]']
    for label, url in item["links"].items():
        parts.append(linker({"doi": "DOI", "pdf": "PDF", "url": "Record", "arxiv": "arXiv"}.get(label, label.title()), url))
    return " ".join(parts)


def render_web(resume, fingerprint):
    parts = ["---", "layout: archive", 'title: "Research Scientist Resume"', "permalink: /cv/research/",
             "author_profile: true", "---", "",
             "<!-- Generated by tools/build_research_resume.py. Edit _data/research_resume.yml,",
             "     _data/cv.yml, _data/publications.yml or _config.yml, then run the generator. -->",
             "{% include base_path %}", "",
             f'<p><a class="button" href="{{{{ base_path }}}}/assets/cv-research-scientist.pdf?v={fingerprint[:16]}" download>Download Research Scientist Resume (PDF)</a></p>',
             f'<p><small>Last updated: {escape(resume["updated"])}</small></p>', "",
             f'<h2>{escape(academic.display_name(resume))}</h2>',
             f'<p><strong>{escape(resume["headline"])}</strong><br>{escape(resume["location"])}</p>',
             '<p>' + " &middot; ".join(academic.link_html(item["label"], item["url"]) for item in resume["contacts"]) + '</p>',
             f'<p>{escape(resume["summary"])}</p>', ""]
    for field, heading in (("experience", "Selected Research Experience"), ("education", "Education"), ("research", "Selected Research")):
        parts.extend([f"## {heading}", ""])
        for item in resume[field]:
            parts.append(f'<p><strong>{escape(item["title"])}</strong> &middot; {escape(item["date"])}'
                         + (f'<br>{escape(item["subtitle"])}' if item["subtitle"] else "") + '</p>')
            if item["bullets"]:
                parts.extend(["<ul>"] + [f"  <li>{escape(bullet)}</li>" for bullet in item["bullets"]] + ["</ul>"])
            parts.append("")
    parts.extend(["## Selected Publications", ""])
    for item in resume["publications"]:
        parts.extend([f"<p>{publication_html(item)}</p>", ""])
    parts.extend(["## Technical Expertise", ""])
    for item in resume["skills"]:
        parts.extend([f'<p><strong>{escape(item["title"])}</strong>: {escape(item["text"])}</p>', ""])
    parts.append('<p>For the complete publication and appointment record, see the <a href="{{ base_path }}/cv/">Academic CV</a>.</p>')
    return "\n".join(parts).rstrip() + "\n"


def styles():
    body = ParagraphStyle("Body", fontName="Helvetica", fontSize=10, leading=13,
                          textColor=colors.HexColor("#243444"), spaceAfter=4,
                          allowOrphans=0, allowWidows=0)
    return {
        "body": body,
        "name": ParagraphStyle("Name", parent=body, fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=NAVY, spaceAfter=5),
        "headline": ParagraphStyle("Headline", parent=body, fontName="Helvetica-Bold", fontSize=11.8, leading=15, textColor=TEAL, spaceAfter=5),
        "contact": ParagraphStyle("Contact", parent=body, fontSize=9, leading=12, spaceAfter=7),
        "section": ParagraphStyle("Section", parent=body, fontName="Helvetica-Bold", fontSize=11.5, leading=14, textColor=NAVY,
                                  spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "entry": ParagraphStyle("Entry", parent=body, fontName="Helvetica-Bold", leading=13, spaceAfter=2, keepWithNext=True),
        "detail": ParagraphStyle("Detail", parent=body, fontSize=9.6, leading=12, textColor=GRAY, spaceAfter=4, keepWithNext=True),
        "bullet": ParagraphStyle("Bullet", parent=body, leftIndent=10, firstLineIndent=0, bulletIndent=0, bulletFontSize=8, spaceAfter=3),
        "publication": ParagraphStyle("Publication", parent=body, fontSize=9.5, leading=12.4, spaceAfter=7),
    }


def render_pdf(resume, fingerprint):
    out, style = BytesIO(), styles()
    document = SimpleDocTemplate(out, pagesize=letter, leftMargin=43, rightMargin=43, topMargin=39, bottomMargin=39,
                                 title=f'{resume["name"]} - Research Scientist Resume', author=resume["name"],
                                 subject=SUBJECT + fingerprint, creator="tools/build_research_resume.py", invariant=1)
    esc = academic.pdf_escape
    contacts = [academic.pdf_link(item["label"], item["url"]) for item in resume["contacts"]]
    story = [Paragraph(esc(academic.display_name(resume)), style["name"]),
             Paragraph(esc(resume["headline"]), style["headline"]),
             Paragraph(esc(resume["location"]) + " &nbsp; | &nbsp; " + " &nbsp; | &nbsp; ".join(contacts), style["contact"]),
             HRFlowable(width="100%", thickness=1, color=TEAL, spaceAfter=9),
             Paragraph(esc(resume["summary"]), style["body"])]

    def heading(text):
        story.append(Paragraph(esc(text), style["section"]))

    def entry(item, education=False):
        parts = [Paragraph(esc(item["title"]) + f' <font name="Helvetica" color="#475569">| {esc(item["date"])}</font>', style["entry"])]
        if item["subtitle"]:
            parts.append(Paragraph(esc(item["subtitle"]), style["detail"]))
        if not education:
            parts.extend(Paragraph(esc(bullet), style["bullet"], bulletText="\u2022") for bullet in item["bullets"])
        # Each concise entry is kept intact; overflow is rejected by the two-page check.
        story.append(KeepTogether(parts))
        story.append(Spacer(1, 3))

    heading("Selected Research Experience")
    for item in resume["experience"]:
        entry(item)
    heading("Education")
    for item in resume["education"]:
        entry(item, education=True)
    story.append(PageBreak())
    heading("Selected Research")
    for item in resume["research"]:
        entry(item)
    heading("Selected Publications")
    for item in resume["publications"]:
        story.append(Paragraph(publication_html(item, pdf=True), style["publication"]))
    heading("Technical Expertise")
    for item in resume["skills"]:
        story.append(Paragraph(f'<b>{esc(item["title"])}</b>: {esc(item["text"])}', style["body"]))

    def decoration(canvas, doc):
        canvas.saveState()
        width, height = letter
        canvas.setStrokeColor(colors.HexColor("#CFDCE3"))
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, 29, width - doc.rightMargin, 29)
        canvas.setFillColor(GRAY)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(doc.leftMargin, 17, academic.pdf_plain(resume["name"]) + " | Research Scientist Resume")
        canvas.drawRightString(width - doc.rightMargin, 17, f'{doc.page} / 2')
        canvas.linkURL(resume["source_url"], (doc.leftMargin, 14, doc.leftMargin + 215, 26), relative=0)
        if doc.page > 1:
            canvas.setFont("Helvetica", 8)
            canvas.drawString(doc.leftMargin, height - 24, academic.pdf_plain(resume["name"]))
            canvas.drawRightString(width - doc.rightMargin, height - 24, "Robotics & Multimodal Perception")
        canvas.restoreState()

    document.build(story, onFirstPage=decoration, onLaterPages=decoration, canvasmaker=partial(Canvas, invariant=1))
    data = out.getvalue()
    signature = academic.pdf_signature(data)
    if signature["pages"] != 2:
        raise ValueError(f'Research resume must fit exactly two pages, but rendered {signature["pages"]}; shorten the narrative before publishing')
    if "Selected Research" not in signature["text"][1]:
        raise ValueError("Selected Research must begin on the second page")
    return data


def check_outputs(root, expected_web, expected_pdf, fingerprint):
    errors = []
    web, pdf = root / WEB_PATH, root / PDF_PATH
    if not web.is_file():
        errors.append(f"{WEB_PATH} is missing")
    elif web.read_text(encoding="utf-8") != expected_web:
        errors.append(f"{WEB_PATH} differs from the current research resume sources")
    if not pdf.is_file():
        errors.append(f"{PDF_PATH} is missing")
    else:
        try:
            actual, expected = academic.pdf_signature(pdf.read_bytes()), academic.pdf_signature(expected_pdf)
            if actual["subject"] != SUBJECT + fingerprint:
                errors.append(f"{PDF_PATH} has a stale or missing source fingerprint")
            if actual["text"] != expected["text"]:
                errors.append(f"{PDF_PATH} content or pagination differs from the current resume sources")
            if actual["uris"] != expected["uris"]:
                errors.append(f"{PDF_PATH} hyperlink destinations differ from the current resume sources")
        except Exception as exc:
            errors.append(f"{PDF_PATH} cannot be validated: {exc}")
    for alias in LEGACY_PDFS:
        if not (root / alias).is_file():
            errors.append(f"{alias} is missing; legacy downloads must alias the current research resume")
        elif pdf.is_file() and (root / alias).read_bytes() != pdf.read_bytes():
            errors.append(f"{alias} differs from the canonical research resume; legacy downloads must have identical content")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Rebuild and commit both generated files with: {REBUILD}", file=sys.stderr)
        return 1
    print(f"Research resume check passed: web and two-page PDF match sources ({fingerprint[:16]}).")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate generated page and PDF without writing files")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: parent of tools)")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        resume = load_sources(root)
        fingerprint = source_fingerprint(root, resume)
        web, pdf = render_web(resume, fingerprint), render_pdf(resume, fingerprint)
        if args.check:
            return check_outputs(root, web, pdf, fingerprint)
        for relative, content in [(WEB_PATH, web.encode("utf-8")), (PDF_PATH, pdf)] + [(alias, pdf) for alias in LEGACY_PDFS]:
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_bytes(content)
        print(f"Generated {WEB_PATH} and {PDF_PATH} (2 pages; sources {fingerprint[:16]}).")
        return 0
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: cannot generate research resume: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
