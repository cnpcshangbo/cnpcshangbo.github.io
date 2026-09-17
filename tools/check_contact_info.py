#!/usr/bin/env python3
"""Keep website and downloadable CV contact details aligned with _config.yml.

Run without arguments for checked-in sources/PDFs, with --site-dir _site for
Jekyll output, or with --live-base-url URL for the deployed pages and PDFs.
"""

import argparse
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, unquote, urljoin, urlsplit
from urllib.request import Request, urlopen

from pypdf import PdfReader
import yaml


ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "/": "_pages/about.md",
    "/cv/": "_pages/cv.md",
    "/resumes/": "_pages/resumes.md",
    "/cv/robotics/": "_pages/cv-robotics.md",
    "/cv/ml/": "_pages/cv-ml.md",
}
EMAIL = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SOURCE_PDF = re.compile(r"(?:https?://[^\s\"'<>\)]+)?/[^\s\"'<>\)]*cv[^/\s\"'<>\)]*\.pdf(?:[?#][^\s\"'<>\)]*)?", re.I)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.text = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.hidden_depth += 1
        for name, value in attrs:
            if name in {"href", "src", "data"} and value:
                self.links.append(value)

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.hidden_depth = max(0, self.hidden_depth - 1)

    def handle_data(self, data):
        if not self.hidden_depth:
            self.text.append(data)


def emails(text):
    return {match.casefold() for match in EMAIL.findall(text)}


def mailto_recipients(uri):
    parsed = urlsplit(uri)
    if parsed.scheme.casefold() != "mailto":
        return None
    recipients = unquote(parsed.path).split(",")
    for name, values in parse_qs(parsed.query).items():
        if name.casefold() in {"to", "cc", "bcc"}:
            for value in values:
                recipients.extend(value.split(","))
    return {recipient.strip().casefold() for recipient in recipients if recipient.strip()}


def validate_contact(label, text, uris, canonical, require_visible=True):
    """Return errors; PDF text and links are deliberately checked separately."""
    canonical = canonical.casefold()
    errors = []
    visible = emails(text)
    if require_visible and canonical not in visible:
        errors.append(f"{label}: visible email {canonical!r} is missing")
    stale = visible - {canonical}
    if stale:
        errors.append(f"{label}: unexpected visible email(s): {', '.join(sorted(stale))}")
    found = False
    for uri in uris:
        recipients = mailto_recipients(uri)
        if recipients is None:
            continue
        found = found or canonical in recipients
        if recipients != {canonical}:
            errors.append(f"{label}: mailto must target {canonical!r}, found {uri!r}")
    if not found:
        errors.append(f"{label}: mailto:{canonical} link is missing")
    return errors


def validate_pdf(label, data, canonical):
    reader = PdfReader(BytesIO(data))
    if not reader.pages:
        return [f"{label}: PDF has no pages"]
    text, uris = [], []
    for page in reader.pages:
        text.append(page.extract_text() or "")
        for annotation in page.get("/Annots", []):
            action = annotation.get_object().get("/A")
            if action:
                uri = action.get_object().get("/URI")
                if uri:
                    uris.append(str(uri))
    return validate_contact(label, "\n".join(text), uris, canonical)


def linked_pdfs(links, page_url, base_url):
    """Discover same-site CV PDF links, including query-string download links."""
    paths = set()
    origin = urlsplit(base_url)
    for link in links:
        target = urlsplit(urljoin(page_url, link))
        path = unquote(target.path)
        if target.netloc != origin.netloc:
            continue
        if re.fullmatch(r"cv[^/]*\.pdf", Path(path).name, re.I):
            paths.add(path)
    return paths


def fetch(url):
    request = Request(url, headers={"User-Agent": "CV-contact-check/1.0", "Cache-Control": "no-cache"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def generated_contact(canonical):
    return "% Generated from _config.yml author.email; do not edit.\n" + f"\\newcommand{{\\cvemail}}{{{canonical}}}\n"


def check_sources(root, canonical, base_url):
    errors, pdfs = [], set()
    contact = root / "cv-tex/contact-info.tex"
    if not contact.is_file() or contact.read_text() != generated_contact(canonical):
        errors.append("cv-tex/contact-info.tex: regenerate the shared contact include from _config.yml author.email")
    sources = sorted((root / "cv-tex").glob("cv*.tex"))
    if not sources:
        errors.append("cv-tex: no CV LaTeX sources found")
    for source in sources:
        text = source.read_text()
        label = str(source.relative_to(root))
        if r"\input{contact-info.tex}" not in text or r"\href{mailto:\cvemail}{\cvemail}" not in text:
            errors.append(f"{label}: use \\input{{contact-info.tex}} and \\href{{mailto:\\cvemail}}{{\\cvemail}}")
        if emails(text):
            errors.append(f"{label}: remove hardcoded email(s); use \\cvemail from the shared include")
        pdfs.add("/assets/" + source.with_suffix(".pdf").name)
    for path, source in PAGES.items():
        file = root / source
        if not file.is_file():
            errors.append(f"{source}: contact page source is missing")
            continue
        text = file.read_text()
        stale = emails(text) - {canonical.casefold()}
        if stale:
            errors.append(f"{source}: unexpected email(s): {', '.join(sorted(stale))}")
        pdfs.update(linked_pdfs(SOURCE_PDF.findall(text), urljoin(base_url, path), base_url))
    return errors, pdfs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--site-dir", type=Path, help="validate built Jekyll HTML and PDF files")
    modes.add_argument("--live-base-url", help="validate deployed HTML and downloadable PDF bytes")
    args = parser.parse_args()
    try:
        config = yaml.safe_load((ROOT / "_config.yml").read_text())
        canonical = config["author"]["email"]
        if not isinstance(canonical, str) or not EMAIL.fullmatch(canonical):
            raise ValueError("author.email must be one valid email address")
        base_url = (args.live_base_url or config["url"]).rstrip("/") + "/"
        if urlsplit(base_url).scheme not in {"http", "https"}:
            raise ValueError("site base URL must use http or https")
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"ERROR _config.yml: {exc}", file=sys.stderr)
        return 1

    errors = []
    pdfs = {"/" + path.relative_to(ROOT).as_posix() for path in (ROOT / "assets").glob("cv*.pdf")}
    if not pdfs:
        errors.append("assets: no cv*.pdf artifacts found")
    if not args.site_dir and not args.live_base_url:
        source_errors, linked = check_sources(ROOT, canonical, base_url)
        errors.extend(source_errors)
        pdfs.update(linked)
    else:
        if args.site_dir:
            pdfs.update("/" + path.relative_to(args.site_dir).as_posix() for path in (args.site_dir / "assets").glob("cv*.pdf"))
        for path in PAGES:
            label = urljoin(base_url, path) if args.live_base_url else str(args.site_dir / path.lstrip("/") / "index.html")
            try:
                data = fetch(label) if args.live_base_url else Path(label).read_bytes()
                page = Page()
                page.feed(data.decode("utf-8"))
                page_errors = validate_contact(label, " ".join(page.text), page.links, canonical, require_visible=False)
                if "Sorry, but the page you were trying to view does not exist" in " ".join(page.text):
                    page_errors.append(f"{label}: page renders the site's 404 content")
                errors.extend(page_errors)
                pdfs.update(linked_pdfs(page.links, urljoin(base_url, path), base_url))
                if not page_errors:
                    print(f"OK {label}: current contact link")
            except Exception as exc:
                errors.append(f"{label}: unable to read/validate HTML: {exc}")

    artifact_root = args.site_dir or ROOT
    for path in sorted(pdfs):
        label = urljoin(base_url, path) if args.live_base_url else str(artifact_root / path.lstrip("/"))
        try:
            data = fetch(label) if args.live_base_url else Path(label).read_bytes()
            pdf_errors = validate_pdf(label, data, canonical)
            errors.extend(pdf_errors)
            if not pdf_errors:
                print(f"OK {label}: visible email and mailto match {canonical}")
        except Exception as exc:
            errors.append(f"{label}: unable to read/validate PDF (missing or invalid artifact): {exc}")

    for error in errors:
        print(f"ERROR {error}", file=sys.stderr)
    if errors:
        print(f"Contact check failed: {len(errors)} error(s). Update the source and rebuild affected PDFs before publishing.", file=sys.stderr)
        return 1
    print(f"Contact check passed: {len(pdfs)} CV PDFs; canonical email is {canonical}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
