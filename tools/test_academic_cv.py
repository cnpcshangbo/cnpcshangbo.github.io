#!/usr/bin/env python3
"""Regression checks for stale academic CV content beyond the contact address."""

from contextlib import redirect_stderr, redirect_stdout
from io import BytesIO, StringIO
from pathlib import Path
import shutil
import tempfile
import unittest

from pypdf import PdfReader, PdfWriter
import yaml

import build_academic_cv as cv_builder


class AcademicCVTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="academic-cv-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for directory in ("_data", "_pages", "assets", "tools"):
            (self.root / directory).mkdir()
        for name in ("build_academic_cv.py", "requirements-academic-cv.txt", "requirements-contact.txt"):
            shutil.copyfile(Path(__file__).with_name(name), self.root / "tools" / name)
        self.config = {
            "url": "https://example.edu", "baseurl": "",
            "author": {"name": "Test Researcher", "email": "current@example.edu"},
        }
        self.cv = {
            "updated": "2026-09-17", "name": "Test Researcher", "credentials": "Ph.D.",
            "headline": "Postdoctoral Associate", "affiliation": "Current University",
            "location": "College Park, MD",
            "sections": [
                {"title": "Appointments", "items": [
                    {"title": "Current University", "date": "2026 - Present",
                     "text": "Develops field robotics and sensor data collection workflows."},
                ]},
                {"title": "Journal Articles", "publication_types": ["journal"], "prefix": "J"},
            ],
        }
        self.publications = {"items": [
            {"title": "An infrastructure inspection study", "authors": "T Researcher, C Hern\u00e1ndez",
             "venue": "Robotics Journal", "year": 2026, "type": "journal",
             "links": {"pdf": "https://example.edu/original-paper.pdf"}},
        ]}
        self.write_sources()
        web, pdf, _ = self.expected()
        (self.root / cv_builder.WEB_PATH).write_text(web, encoding="utf-8")
        (self.root / cv_builder.PDF_PATH).write_bytes(pdf)

    def write_sources(self):
        for relative, source in (("_config.yml", self.config), ("_data/cv.yml", self.cv),
                                 ("_data/publications.yml", self.publications)):
            (self.root / relative).write_text(yaml.safe_dump(source, allow_unicode=True, sort_keys=False), encoding="utf-8")

    def expected(self):
        data = cv_builder.load_sources(self.root)
        fingerprint = cv_builder.source_fingerprint(self.root, data)
        return cv_builder.render_web(data, fingerprint), cv_builder.render_pdf(data, fingerprint), fingerprint

    def check(self, expected):
        output, errors = StringIO(), StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            result = cv_builder.check_outputs(self.root, *expected)
        return result, errors.getvalue()

    def refresh_web_and_metadata_only(self, expected):
        """Simulate a misleading refresh that leaves actual PDF content/links stale."""
        web, _, fingerprint = expected
        (self.root / cv_builder.WEB_PATH).write_text(web, encoding="utf-8")
        reader = PdfReader(self.root / cv_builder.PDF_PATH)
        writer = PdfWriter()
        writer.clone_document_from_reader(reader)
        writer.add_metadata({"/Subject": f"Academic CV source SHA256: {fingerprint}"})
        output = BytesIO()
        writer.write(output)
        (self.root / cv_builder.PDF_PATH).write_bytes(output.getvalue())

    def test_current_generated_fixture_passes(self):
        expected = self.expected()
        self.assertEqual(self.check(expected), (0, ""))
        actual = (self.root / cv_builder.PDF_PATH).read_bytes()
        self.assertEqual(actual, expected[1], "ReportLab invariant output must be reproducible")
        self.assertIn("Hern\u00e1ndez", " ".join(cv_builder.pdf_signature(actual)["text"]))

    def test_changed_appointment_body_rejects_pdf_with_current_email(self):
        self.cv["sections"][0]["items"][0]["text"] = "Leads newly appointed field deployment and sensor calibration research."
        self.write_sources()
        expected = self.expected()
        self.refresh_web_and_metadata_only(expected)
        actual = cv_builder.pdf_signature((self.root / cv_builder.PDF_PATH).read_bytes())
        self.assertIn("current@example.edu", " ".join(actual["text"]))
        result, errors = self.check(expected)
        self.assertEqual(result, 1)
        self.assertIn("content or pagination differs", errors)
        self.assertNotIn("source fingerprint", errors)
        self.assertNotIn("hyperlink destinations", errors)

    def test_changed_uri_rejects_pdf_with_identical_visible_text(self):
        self.publications["items"][0]["links"]["pdf"] = "https://example.edu/corrected-paper.pdf"
        self.write_sources()
        expected = self.expected()
        self.refresh_web_and_metadata_only(expected)
        actual = cv_builder.pdf_signature((self.root / cv_builder.PDF_PATH).read_bytes())
        self.assertEqual(actual["text"], cv_builder.pdf_signature(expected[1])["text"])
        result, errors = self.check(expected)
        self.assertEqual(result, 1)
        self.assertIn("hyperlink destinations differ", errors)
        self.assertNotIn("content or pagination", errors)
        self.assertNotIn("source fingerprint", errors)

    def test_new_unassigned_publication_type_requires_explicit_cv_section(self):
        self.publications["items"].append({
            "title": "A new patent", "authors": "T Researcher", "venue": "US Patent 123",
            "year": 2026, "type": "patent",
        })
        self.write_sources()
        with self.assertRaisesRegex(ValueError, "Publications would be omitted.*patent"):
            cv_builder.load_sources(self.root)


if __name__ == "__main__":
    unittest.main()
