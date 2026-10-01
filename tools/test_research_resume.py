"""Guard the resume's canonical facts, downloadable content, and two-page limit."""

from contextlib import redirect_stderr, redirect_stdout
from io import BytesIO, StringIO
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from pypdf import PdfReader, PdfWriter
import yaml

import build_research_resume as builder


class ResearchResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ("tools", "_data", "_pages", "assets"):
            (self.root / directory).mkdir()
        for relative in ("tools/build_research_resume.py", "tools/build_academic_cv.py",
                         "tools/requirements-academic-cv.txt", "tools/requirements-contact.txt"):
            shutil.copyfile(builder.ROOT / relative, self.root / relative)
        self.config = {"url": "https://example.edu", "baseurl": "", "author": {"name": "Test Researcher", "email": "current@example.edu"}}
        self.cv = {
            "updated": "2026-10-01", "name": "Test Researcher", "credentials": "Ph.D.",
            "headline": "Postdoctoral Associate", "affiliation": "Example University", "location": "New York, NY",
            "sections": [
                {"title": "Academic and Research Appointments", "items": [{"title": "Example University", "subtitle": "Postdoctoral Associate", "date": "2026 - Present"}]},
                {"title": "Education", "items": [{"title": "Prior University", "subtitle": "Ph.D., Robotics", "date": "2020"}]},
                {"title": "Research and Engineering Projects", "items": [{"title": "Field perception", "date": "2025 - 2026"}]},
                {"title": "Journal Articles", "publication_types": ["journal"]},
            ],
        }
        self.publications = {"items": [{"title": "Field Robotics Study", "authors": "T Researcher, C Hernández", "venue": "Example Journal", "year": 2026, "type": "journal", "links": {"doi": "https://doi.org/example"}}]}
        self.source = {
            "updated": "2026-10-01", "headline": "Research Scientist | Robotics & Multimodal Perception", "summary": "Researcher building reliable perception for field robots.",
            "experience": [{"appointment": "Postdoctoral Associate", "bullets": ["Developed a sensor evaluation workflow."]}],
            "education": ["Ph.D., Robotics"],
            "research": [{"project": "Field perception", "bullets": ["Evaluated sensor calibration across field sites."]}],
            "publications": ["Field Robotics Study"], "skills": [{"title": "Robotics", "text": "ROS, LiDAR, Python."}],
        }
        self.write_sources()
        self.write_outputs(self.expected())

    def write_sources(self):
        for relative, data in (("_config.yml", self.config), ("_data/cv.yml", self.cv),
                               ("_data/publications.yml", self.publications), ("_data/research_resume.yml", self.source)):
            (self.root / relative).write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))

    def expected(self):
        resume = builder.load_sources(self.root)
        fingerprint = builder.source_fingerprint(self.root, resume)
        return builder.render_web(resume, fingerprint), builder.render_pdf(resume, fingerprint), fingerprint

    def write_outputs(self, expected):
        web, pdf, _ = expected
        (self.root / builder.WEB_PATH).write_text(web)
        for relative in (builder.PDF_PATH, *builder.LEGACY_PDFS):
            (self.root / relative).write_bytes(pdf)

    def check(self, expected):
        output = StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            result = builder.check_outputs(self.root, *expected)
        return result, output.getvalue()

    def forge_current_metadata(self, expected):
        """Current metadata alone must not make stale PDF content pass."""
        web, _, fingerprint = expected
        (self.root / builder.WEB_PATH).write_text(web)
        writer = PdfWriter()
        writer.clone_document_from_reader(PdfReader(self.root / builder.PDF_PATH))
        writer.add_metadata({"/Subject": builder.SUBJECT + fingerprint})
        stream = BytesIO()
        writer.write(stream)
        for relative in (builder.PDF_PATH, *builder.LEGACY_PDFS):
            (self.root / relative).write_bytes(stream.getvalue())

    def test_current_outputs_have_two_pages_and_canonical_facts(self):
        expected = self.expected()
        self.assertEqual(self.check(expected)[0], 0)
        signature = builder.academic.pdf_signature(expected[1])
        self.assertEqual(signature["pages"], 2)
        self.assertIn("Postdoctoral Associate", signature["text"][0])
        self.assertIn("Selected Research", signature["text"][1])
        self.assertIn("Hernández", signature["text"][1])
        self.assertEqual((self.root / builder.PDF_PATH).read_bytes(), expected[1])
        self.assertIn("mailto:current@example.edu", signature["uris"])

    def test_canonical_date_change_rejects_stale_pdf_despite_current_metadata(self):
        self.cv["sections"][0]["items"][0]["date"] = "2025 - Present"
        self.write_sources()
        expected = self.expected()
        self.forge_current_metadata(expected)
        status, errors = self.check(expected)
        self.assertEqual(status, 1)
        self.assertIn("content or pagination differs", errors)
        self.assertNotIn("source fingerprint", errors)

    def test_link_change_rejected_even_when_text_and_metadata_match(self):
        self.publications["items"][0]["links"]["doi"] = "https://doi.org/corrected"
        self.write_sources()
        expected = self.expected()
        self.forge_current_metadata(expected)
        status, errors = self.check(expected)
        self.assertEqual(status, 1)
        self.assertIn("hyperlink destinations differ", errors)
        self.assertNotIn("content or pagination differs", errors)

    def test_legacy_resume_variant_cannot_diverge_from_canonical_pdf(self):
        (self.root / builder.LEGACY_PDFS[0]).write_bytes(b"old role-specific resume")
        status, errors = self.check(self.expected())
        self.assertEqual(status, 1)
        self.assertIn("legacy downloads must have identical content", errors)

    def test_missing_and_ambiguous_appointments_fail_instead_of_guessing(self):
        self.source["experience"][0]["appointment"] = "Assistant Research Scientist"
        self.write_sources()
        with self.assertRaisesRegex(ValueError, "found 0"):
            builder.load_sources(self.root)
        self.source["experience"][0]["appointment"] = "Postdoctoral Associate"
        self.cv["sections"][0]["items"] *= 2
        self.write_sources()
        with self.assertRaisesRegex(ValueError, "found 2"):
            builder.load_sources(self.root)

    def test_overflow_fails_instead_of_silently_publishing_more_pages(self):
        self.source["research"][0]["bullets"] = ["Long research narrative across sensors and field sites. " * 8] * 24
        self.write_sources()
        with self.assertRaisesRegex(ValueError, "must fit exactly two pages"):
            self.expected()

    def test_missing_pdf_is_a_failure(self):
        (self.root / builder.PDF_PATH).unlink()
        status, errors = self.check(self.expected())
        self.assertEqual(status, 1)
        self.assertIn("is missing", errors)


if __name__ == "__main__":
    unittest.main()
