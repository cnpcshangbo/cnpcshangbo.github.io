#!/usr/bin/env python3
"""Generate the academic CV page and PDF from their shared, structured sources.

Run after editing _data/cv.yml, _data/publications.yml, or canonical contact
information in _config.yml. Use --check in CI to reject missing/stale output.
The check compares readable PDF content and hyperlinks, not platform-specific
PDF bytes, and also verifies a fingerprint of sources and renderer code.
"""

import argparse
from datetime import date
from functools import partial
from hashlib import sha256
from html import escape
from io import BytesIO
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import urlsplit

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
import yaml


ROOT = Path(__file__).resolve().parents[1]
WEB_PATH = Path("_pages/cv.md")
PDF_PATH = Path("assets/cv.pdf")
REBUILD = "python tools/build_academic_cv.py"
ENTRY_FIELDS = ("title", "subtitle", "date", "location", "text", "bullets", "links")
TYPE_LABELS = {
    "journal": "Journal Articles",
    "conference": "Conference Papers",
    "preprint": "Preprints",
    "patent": "Patents",
    "report": "Technical Reports",
    "thesis": "Theses",
    "poster": "Posters",
    "slides": "Presentation Slides",
}
TYPE_PREFIXES = {
    "journal": "J", "conference": "C", "preprint": "P", "patent": "PT",
    "report": "R", "thesis": "T", "poster": "PO", "slides": "S",
}
NAVY = colors.HexColor("#17354B")
TEAL = colors.HexColor("#146B74")
GRAY = colors.HexColor("#475569")
DASHES = str.maketrans({char: "-" for char in "\u2010\u2011\u2012\u2013\u2014\u2212"})


def string(value, label, required=False):
    if value is None and not required:
        return ""
    if not isinstance(value, str) or (required and not value.strip()):
        raise ValueError(f"{label} must be {'a nonempty' if required else 'a'} string")
    return value.strip()


def mapping(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a mapping")
    return value


def http_url(value, label):
    value = string(value, label, required=True)
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or any(char.isspace() for char in value):
        raise ValueError(f"{label} must be an absolute HTTP(S) URL")
    return value


def links(value, label):
    if value is None:
        return {}
    selected = {
        string(key, f"{label} label", required=True): http_url(url, f"{label}.{key}")
        for key, url in mapping(value, label).items()
    }
    return {key: selected[key] for key in sorted(selected)}


def load_yaml(path):
    return mapping(yaml.safe_load(path.read_text(encoding="utf-8")), str(path))


def load_sources(root):
    """Validate and select only public fields used in the rendered CV."""
    config = load_yaml(root / "_config.yml")
    source = load_yaml(root / "_data/cv.yml")
    publication_source = load_yaml(root / "_data/publications.yml")
    author = mapping(config.get("author"), "_config.yml author")
    name = string(author.get("name"), "author.name", required=True)
    if string(source.get("name"), "cv.name", required=True) != name:
        raise ValueError("cv.name must match canonical _config.yml author.name")
    email = string(author.get("email"), "author.email", required=True)
    if not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email):
        raise ValueError("author.email must contain one valid email address")
    updated = source.get("updated")
    if isinstance(updated, date):
        updated = updated.isoformat()
    updated = string(updated, "cv.updated", required=True)
    if date.fromisoformat(updated).isoformat() != updated:
        raise ValueError("cv.updated must have YYYY-MM-DD format")

    site_url = http_url(config.get("url"), "_config.yml url").rstrip("/")
    baseurl = string(config.get("baseurl"), "_config.yml baseurl")
    if baseurl and (not baseurl.startswith("/") or "?" in baseurl or "#" in baseurl):
        raise ValueError("baseurl must be empty or an absolute URL path")
    site_url += baseurl.rstrip("/")
    contacts = [{"label": email, "url": "mailto:" + email}]
    phone = string(source.get("phone"), "cv.phone")
    if phone:
        telephone = re.sub(r"[\s().-]", "", phone)
        if not re.fullmatch(r"\+?\d{7,15}", telephone):
            raise ValueError("cv.phone must be a public telephone number")
        contacts.append({"label": phone, "url": "tel:" + telephone})
    contacts.append({"label": "Website", "url": site_url + "/"})
    for field, label in (("googlescholar", "Google Scholar"), ("orcid", "ORCID")):
        if author.get(field):
            contacts.append({"label": label, "url": http_url(author[field], f"author.{field}")})

    cv = {"name": name, "updated": updated}
    for field in ("credentials", "headline", "affiliation", "location", "summary"):
        cv[field] = string(source.get(field), f"cv.{field}", required=field in {"headline", "affiliation", "location"})
    cv["contacts"] = contacts
    cv["source_url"] = site_url + "/cv/"

    raw_publications = publication_source.get("items")
    if not isinstance(raw_publications, list):
        raise ValueError("publications.items must be a list")
    publications = []
    for index, raw in enumerate(raw_publications):
        label = f"publications.items[{index}]"
        raw = mapping(raw, label)
        if "cv_exclude" in raw and not isinstance(raw["cv_exclude"], bool):
            raise ValueError(f"{label}.cv_exclude must be true or false")
        if raw.get("cv_exclude", False):
            continue
        item = {field: string(raw.get(field), f"{label}.{field}", required=field != "note")
                for field in ("title", "authors", "venue", "type", "note")}
        year = raw.get("year")
        if isinstance(year, bool) or not isinstance(year, int) or not 1900 <= year <= 2200:
            raise ValueError(f"{label}.year must be an integer from 1900 through 2200")
        item["year"] = year
        item["links"] = links(raw.get("links"), f"{label}.links")
        publications.append(item)

    raw_sections = source.get("sections")
    if not isinstance(raw_sections, list) or not raw_sections:
        raise ValueError("cv.sections must be a nonempty list")
    sections, assigned_types = [], set()
    for index, raw in enumerate(raw_sections):
        label = f"cv.sections[{index}]"
        raw = mapping(raw, label)
        section = {"title": string(raw.get("title"), f"{label}.title", required=True)}
        if ("items" in raw) == ("publication_types" in raw):
            raise ValueError(f"{label} must contain exactly one of items or publication_types")
        if "publication_types" in raw:
            types = raw["publication_types"]
            if not isinstance(types, list) or not types:
                raise ValueError(f"{label}.publication_types must be a nonempty list")
            groups = []
            for kind in types:
                kind = string(kind, f"{label}.publication_types", required=True)
                if kind not in TYPE_LABELS:
                    raise ValueError(f"Unknown publication type {kind!r}; add an explicit heading and prefix to this renderer")
                if kind in assigned_types:
                    raise ValueError(f"Publication type {kind!r} is assigned to multiple CV sections")
                assigned_types.add(kind)
                prefix = string(raw.get("prefix", TYPE_PREFIXES[kind]), f"{label}.prefix", required=True)
                entries = sorted((item for item in publications if item["type"] == kind),
                                 key=lambda item: item["year"], reverse=True)
                groups.append({"title": TYPE_LABELS[kind], "type": kind, "prefix": prefix, "items": entries})
            section["groups"] = groups
        else:
            if not isinstance(raw["items"], list) or not raw["items"]:
                raise ValueError(f"{label}.items must be a nonempty list")
            section["items"] = []
            for entry_index, entry in enumerate(raw["items"]):
                entry_label = f"{label}.items[{entry_index}]"
                entry = mapping(entry, entry_label)
                item = {field: string(entry.get(field), f"{entry_label}.{field}")
                        for field in ENTRY_FIELDS if field not in {"bullets", "links"}}
                raw_bullets = entry.get("bullets", [])
                if not isinstance(raw_bullets, list):
                    raise ValueError(f"{entry_label}.bullets must be a list")
                item["bullets"] = [string(bullet, f"{entry_label}.bullets", required=True) for bullet in raw_bullets]
                item["links"] = links(entry.get("links"), f"{entry_label}.links")
                if not any(item.values()):
                    raise ValueError(f"{entry_label} must contain visible content")
                section["items"].append(item)
        sections.append(section)
    unassigned = {item["type"] for item in publications} - assigned_types
    if unassigned:
        raise ValueError("Publications would be omitted from the CV: add publication_types sections for "
                         + ", ".join(sorted(unassigned)))
    cv["sections"] = sections
    return cv


def source_fingerprint(root, cv):
    """Include rendered source fields, renderer code, and dependency pins."""
    digest = sha256()
    digest.update(json.dumps(cv, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    for relative in ("tools/build_academic_cv.py", "tools/requirements-academic-cv.txt", "tools/requirements-contact.txt"):
        digest.update(b"\0" + relative.encode("ascii") + b"\0")
        digest.update((root / relative).read_bytes())
    return digest.hexdigest()


def link_html(label, url):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def display_name(cv):
    return cv["name"] + (", " + cv["credentials"] if cv["credentials"] else "")


def publication_html(item, prefix, number, pdf=False):
    esc = pdf_escape if pdf else escape
    linker = pdf_link if pdf else link_html
    parts = [f'[{esc(prefix)}{number}] {esc(item["authors"])}.',
             f'<b>{esc(item["title"].rstrip("."))}.</b>',
             f'<i>{esc(item["venue"].rstrip("."))}</i>, {item["year"]}.']
    if item["note"]:
        parts.append(esc(item["note"].rstrip(".")) + ".")
    parts.extend(linker({"doi": "DOI", "pdf": "PDF", "url": "Record", "arxiv": "arXiv", "ssrn": "SSRN"}.get(label, label.title()), url)
                 for label, url in item["links"].items())
    return " ".join(parts)


def render_web(cv, fingerprint):
    parts = ["---", "layout: archive", 'title: "CV"', "permalink: /cv/", "author_profile: true",
             "redirect_from:", "  - /resume", "---", "",
             "<!-- Generated by tools/build_academic_cv.py. Edit _data/cv.yml, _data/publications.yml,",
             "     or _config.yml instead, then run the generator. -->",
             "{% include base_path %}", "",
             f'<p><a class="button" href="{{{{ base_path }}}}/assets/cv.pdf?v={fingerprint[:16]}" download>Download PDF</a></p>',
             f'<p><small>Last updated: {escape(cv["updated"])}</small></p>', "",
             f'<h2>{escape(display_name(cv))}</h2>',
             f'<p><strong>{escape(cv["headline"])}</strong><br>{escape(cv["affiliation"])}<br>{escape(cv["location"])}</p>',
             '<p>' + " &middot; ".join(link_html(item["label"], item["url"]) for item in cv["contacts"]) + '</p>', ""]
    if cv["summary"]:
        parts.extend([f'<p>{escape(cv["summary"])}</p>', ""])
    for section in cv["sections"]:
        parts.extend([f'## {section["title"]}', ""])
        if "groups" in section:
            for group in section["groups"]:
                if len(section["groups"]) > 1:
                    parts.extend([f'### {group["title"]}', ""])
                for number, item in enumerate(group["items"], 1):
                    parts.extend([f'<p>{publication_html(item, group["prefix"], number)}</p>', ""])
        else:
            for item in section["items"]:
                heading = []
                if item["title"]:
                    heading.append(f'<strong>{escape(item["title"])}</strong>')
                if item["date"]:
                    heading.append(escape(item["date"]))
                details = [escape(item[key]) for key in ("subtitle", "location") if item[key]]
                if heading or details:
                    parts.append('<p>' + " &middot; ".join(heading)
                                 + ('<br>' if heading and details else '') + ' &middot; '.join(details) + '</p>')
                if item["text"]:
                    parts.append(f'<p>{escape(item["text"])}</p>')
                if item["bullets"]:
                    parts.extend(['<ul>'] + [f'  <li>{escape(bullet)}</li>' for bullet in item["bullets"]] + ['</ul>'])
                if item["links"]:
                    parts.append('<p>' + ' &middot; '.join(link_html(label, url) for label, url in item["links"].items()) + '</p>')
                parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def pdf_plain(value):
    """Keep Times base14 text legible; reject silent missing-glyph fallbacks."""
    value = unicodedata.normalize("NFC", str(value)).translate(DASHES).replace("\u00a0", " ")
    try:
        value.encode("cp1252")
    except UnicodeEncodeError as exc:
        unsupported = sorted({char for char in value if not char.isascii() and not _cp1252(char)})
        raise ValueError(f"PDF Times font cannot render {unsupported!r}; spell out these characters or add a portable embedded font") from exc
    return value


def _cp1252(char):
    try:
        char.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


def pdf_escape(value):
    return escape(pdf_plain(value), quote=True)


def pdf_link(label, url):
    return f'<a href="{escape(url, quote=True)}" color="#146B74">{pdf_escape(label)}</a>'


def styles():
    body = ParagraphStyle("Body", fontName="Times-Roman", fontSize=10.3, leading=12.8,
                          textColor=colors.HexColor("#1D2730"), alignment=TA_LEFT,
                          spaceAfter=3.5, allowOrphans=0, allowWidows=0)
    return {
        "body": body,
        "name": ParagraphStyle("Name", parent=body, fontName="Times-Bold", fontSize=25, leading=29,
                               textColor=NAVY, spaceAfter=4, keepWithNext=True),
        "headline": ParagraphStyle("Headline", parent=body, fontName="Times-Bold", fontSize=11.5,
                                   leading=14.5, spaceAfter=2, keepWithNext=True),
        "header": ParagraphStyle("Header", parent=body, fontSize=10, leading=12.5, spaceAfter=2, keepWithNext=True),
        "contact": ParagraphStyle("Contact", parent=body, fontSize=9.3, leading=12, spaceAfter=7),
        "section": ParagraphStyle("Section", parent=body, fontName="Helvetica-Bold", fontSize=12,
                                  leading=15, textColor=NAVY, spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "subsection": ParagraphStyle("Subsection", parent=body, fontName="Times-Bold", fontSize=11,
                                     leading=14, textColor=TEAL, spaceBefore=7, spaceAfter=4, keepWithNext=True),
        "entry": ParagraphStyle("Entry", parent=body, fontName="Times-Bold", spaceAfter=1.8),
        "detail": ParagraphStyle("Detail", parent=body, textColor=GRAY, fontSize=10, leading=12.8, spaceAfter=3),
        "bullet": ParagraphStyle("Bullet", parent=body, leftIndent=10, firstLineIndent=0,
                                 bulletIndent=0, bulletFontName="Times-Roman", bulletFontSize=9, spaceAfter=3),
        "publication": ParagraphStyle("Publication", parent=body, leftIndent=25, firstLineIndent=-25, spaceAfter=6),
        "links": ParagraphStyle("Links", parent=body, fontSize=9.3, leading=12, spaceAfter=3),
    }


def render_pdf(cv, fingerprint):
    out = BytesIO()
    document = SimpleDocTemplate(out, pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
                                 topMargin=17 * mm, bottomMargin=18 * mm,
                                 title=f'{cv["name"]} - Curriculum Vitae', author=cv["name"],
                                 subject=f"Academic CV source SHA256: {fingerprint}",
                                 creator="tools/build_academic_cv.py", pageCompression=1, invariant=1)
    style = styles()
    story = [Paragraph(pdf_escape(display_name(cv)), style["name"]),
             Paragraph(pdf_escape(cv["headline"]), style["headline"]),
             Paragraph(pdf_escape(cv["affiliation"]), style["header"]),
             Paragraph(pdf_escape(cv["location"]), style["header"]),
             Paragraph(" &nbsp; | &nbsp; ".join(pdf_link(item["label"], item["url"]) for item in cv["contacts"]), style["contact"]),
             HRFlowable(width="100%", thickness=0.8, color=TEAL, spaceAfter=7)]
    if cv["summary"]:
        story.append(Paragraph(pdf_escape(cv["summary"]), style["body"]))
    for section in cv["sections"]:
        story.append(Paragraph(pdf_escape(section["title"]), style["section"]))
        if "groups" in section:
            for group in section["groups"]:
                if len(section["groups"]) > 1:
                    story.append(Paragraph(pdf_escape(group["title"]), style["subsection"]))
                for number, item in enumerate(group["items"], 1):
                    story.append(Paragraph(publication_html(item, group["prefix"], number, pdf=True), style["publication"]))
        else:
            for item in section["items"]:
                heading_parts = []
                if item["title"]:
                    heading_parts.append(pdf_escape(item["title"]))
                if item["date"]:
                    heading_parts.append(f'<font name="Times-Roman" color="#475569">{pdf_escape(item["date"])}</font>')
                heading_paragraphs = []
                if heading_parts:
                    heading_paragraphs.append(Paragraph(" &nbsp; | &nbsp; ".join(heading_parts), style["entry"]))
                details = [pdf_escape(item[key]) for key in ("subtitle", "location") if item[key]]
                if details:
                    heading_paragraphs.append(Paragraph(" | ".join(details), style["detail"]))
                content_paragraphs = []
                if item["text"]:
                    content_paragraphs.append(Paragraph(pdf_escape(item["text"]), style["body"]))
                for bullet in item["bullets"]:
                    content_paragraphs.append(Paragraph(pdf_escape(bullet), style["bullet"], bulletText="\u2022"))
                if item["links"]:
                    content_paragraphs.append(Paragraph(" &nbsp; | &nbsp; ".join(pdf_link(label, url) for label, url in item["links"].items()), style["links"]))
                for paragraph in heading_paragraphs[:-1]:
                    paragraph.keepWithNext = True
                if heading_paragraphs and content_paragraphs:
                    heading_paragraphs[-1].keepWithNext = True
                story.extend(heading_paragraphs + content_paragraphs)
                story.append(Spacer(1, 4))

    def page_decoration(canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setStrokeColor(colors.HexColor("#D2DEE5"))
        canvas.setLineWidth(0.4)
        canvas.line(doc.leftMargin, 14 * mm, width - doc.rightMargin, 14 * mm)
        canvas.setFillColor(GRAY)
        canvas.setFont("Times-Roman", 8)
        canvas.drawString(doc.leftMargin, 10 * mm, pdf_plain(f'{cv["name"]} | Curriculum Vitae'))
        canvas.drawCentredString(width / 2, 10 * mm, f'Updated {cv["updated"]}')
        canvas.drawRightString(width - doc.rightMargin, 10 * mm, f"Page {doc.page}")
        # Every page offers a durable link to the live CV, including printed-to-PDF copies.
        canvas.linkURL(cv["source_url"], (doc.leftMargin, 8.8 * mm, doc.leftMargin + 145, 13 * mm), relative=0)
        if doc.page > 1:
            canvas.setFont("Times-Italic", 8)
            canvas.drawString(doc.leftMargin, height - 10.5 * mm, pdf_plain(cv["name"]))
            canvas.drawRightString(width - doc.rightMargin, height - 10.5 * mm, "Curriculum Vitae")
        canvas.restoreState()

    document.build(story, onFirstPage=page_decoration, onLaterPages=page_decoration,
                   canvasmaker=partial(Canvas, invariant=1))
    return out.getvalue()


def pdf_signature(data):
    """Compare content in reading order and actual link annotation destinations."""
    reader = PdfReader(BytesIO(data))
    if not reader.pages:
        raise ValueError("PDF has no pages")
    text, uris = [], set()
    for page in reader.pages:
        text.append(re.sub(r"\s+", " ", unicodedata.normalize("NFKC", page.extract_text() or "")).strip())
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A")
            if action and action.get_object().get("/URI"):
                uris.add(str(action.get_object()["/URI"]))
    return {"text": text, "uris": uris, "subject": str((reader.metadata or {}).get("/Subject", "")),
            "pages": len(reader.pages)}


def check_outputs(root, expected_web, expected_pdf, fingerprint):
    errors = []
    web_path, pdf_path = root / WEB_PATH, root / PDF_PATH
    if not web_path.is_file():
        errors.append(f"{WEB_PATH} is missing")
    elif web_path.read_text(encoding="utf-8") != expected_web:
        errors.append(f"{WEB_PATH} differs from the shared CV data or generated download fingerprint")
    expected = pdf_signature(expected_pdf)
    if not pdf_path.is_file():
        errors.append(f"{PDF_PATH} is missing")
    else:
        try:
            actual = pdf_signature(pdf_path.read_bytes())
            if actual["subject"] != f"Academic CV source SHA256: {fingerprint}":
                errors.append(f"{PDF_PATH} has a stale or missing source fingerprint")
            if actual["text"] != expected["text"]:
                errors.append(f"{PDF_PATH} content or pagination differs from the current CV sources")
            if actual["uris"] != expected["uris"]:
                errors.append(f"{PDF_PATH} hyperlink destinations differ from the current CV sources")
        except Exception as exc:
            errors.append(f"{PDF_PATH} cannot be validated: {exc}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Rebuild and commit both generated files with: {REBUILD}", file=sys.stderr)
        return 1
    print(f"Academic CV check passed: web and {expected['pages']}-page PDF match sources ({fingerprint[:16]}).")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate generated page and PDF without writing files")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: parent of tools)")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        cv = load_sources(root)
        fingerprint = source_fingerprint(root, cv)
        web = render_web(cv, fingerprint)
        pdf = render_pdf(cv, fingerprint)
        if args.check:
            return check_outputs(root, web, pdf, fingerprint)
        (root / WEB_PATH).parent.mkdir(parents=True, exist_ok=True)
        (root / PDF_PATH).parent.mkdir(parents=True, exist_ok=True)
        (root / WEB_PATH).write_text(web, encoding="utf-8")
        (root / PDF_PATH).write_bytes(pdf)
        pages = pdf_signature(pdf)["pages"]
        print(f"Generated {WEB_PATH} and {PDF_PATH} ({pages} pages; sources {fingerprint[:16]}).")
        return 0
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR: cannot generate academic CV: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
