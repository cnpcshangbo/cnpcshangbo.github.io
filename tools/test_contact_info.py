"""Regression cases for failures that HTTP-only PDF checks cannot detect."""

from io import BytesIO
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from pypdf import PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, NumberObject, DecodedStreamObject, TextStringObject

import check_contact_info
from check_contact_info import Page, linked_pdfs, read_contact_page, validate_contact, validate_pdf


CURRENT = "bshang@umd.edu"
OLD = "bshang@ccny.cuny.edu"


def pdf_bytes(visible, target):
    writer = PdfWriter()
    page = writer.add_blank_page(612, 792)
    font = DictionaryObject({NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"), NameObject("/BaseFont"): NameObject("/Helvetica")})
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})})
    content = DecodedStreamObject()
    content.set_data(f"BT /F1 12 Tf 20 750 Td ({visible}) Tj ET".encode())
    page[NameObject("/Contents")] = writer._add_object(content)
    annotation = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Link"),
        NameObject("/Rect"): ArrayObject([NumberObject(n) for n in (20, 740, 300, 755)]),
        NameObject("/A"): DictionaryObject({NameObject("/S"): NameObject("/URI"), NameObject("/URI"): TextStringObject("mailto:" + target)}),
    })
    page[NameObject("/Annots")] = ArrayObject([writer._add_object(annotation)])
    result = BytesIO()
    writer.write(result)
    return result.getvalue()


class ContactCheckTests(unittest.TestCase):
    def test_pdf_current_text_and_link_pass(self):
        self.assertEqual(validate_pdf("CV", pdf_bytes(CURRENT, CURRENT), CURRENT), [])

    def test_pdf_stale_click_target_fails_even_if_text_is_current(self):
        errors = validate_pdf("CV", pdf_bytes(CURRENT, OLD), CURRENT)
        self.assertTrue(any("mailto must target" in error for error in errors))

    def test_pdf_stale_visible_address_fails_even_if_link_is_current(self):
        errors = validate_pdf("CV", pdf_bytes(OLD, CURRENT), CURRENT)
        self.assertTrue(any("unexpected visible email" in error for error in errors))

    def test_pdf_unextractable_email_fails(self):
        errors = validate_pdf("CV", pdf_bytes("Contact me", CURRENT), CURRENT)
        self.assertTrue(any("visible email" in error for error in errors))

    def test_encoded_mailto_and_extra_recipient(self):
        page = Page()
        page.feed('<a href="mailto:bshang%40umd.edu?cc=bshang%40ccny.cuny.edu">Email</a>')
        errors = validate_contact("HTML", " ".join(page.text), page.links, CURRENT, require_visible=False)
        self.assertTrue(any("mailto must target" in error for error in errors))

    def test_linked_cv_discovery_includes_unlisted_variants(self):
        paths = linked_pdfs(
            ["/downloads/cv-new-role.pdf?download=1", "../../assets/cv.pdf", "/assets/paper.pdf", "https://example.org/cv.pdf"],
            "https://cnpcshangbo.github.io/cv/ml/",
            "https://cnpcshangbo.github.io/",
        )
        self.assertEqual(paths, {"/downloads/cv-new-role.pdf", "/assets/cv.pdf"})

    def test_static_redirect_checks_final_contact_and_pdf(self):
        pages = {
            "https://example.org/cv/ml/": b'<meta http-equiv="refresh" content="0; url=/cv/research/">',
            "https://example.org/cv/research/": f'<a href="mailto:{OLD}">Email</a><a href="/assets/cv-research-scientist.pdf">PDF</a>'.encode(),
        }
        with patch.object(check_contact_info, "fetch", side_effect=lambda url: pages[url]):
            label, page, url = read_contact_page("/cv/ml/", "https://example.org/")
        self.assertEqual(url, "https://example.org/cv/research/")
        self.assertTrue(validate_contact(label, " ".join(page.text), page.links, CURRENT, require_visible=False))
        self.assertEqual(linked_pdfs(page.links, url, "https://example.org/"), {"/assets/cv-research-scientist.pdf"})

    def test_static_redirect_cannot_mask_cycle_or_offsite_target(self):
        for target, message in (("/cv/ml/", "cycle"), ("https://other.org/cv/", "outside the website")):
            with self.subTest(target=target):
                with patch.object(check_contact_info, "fetch", return_value=f'<meta http-equiv="refresh" content="0; url={target}">'.encode()):
                    with self.assertRaisesRegex(ValueError, message):
                        read_contact_page("/cv/ml/", "https://example.org/")

    def test_missing_linked_pdf_is_a_failure(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "_config.yml").write_text(f"url: https://example.org\nauthor:\n  email: {CURRENT}\n")
            (root / "assets").mkdir()
            (root / "assets/cv.pdf").write_bytes(pdf_bytes(CURRENT, CURRENT))
            for path in check_contact_info.PAGES:
                page = root / path.lstrip("/") / "index.html"
                page.parent.mkdir(parents=True, exist_ok=True)
                page.write_text(f'<a href="mailto:{CURRENT}">Email</a><a href="/assets/cv-missing.pdf">Download</a>')
            output = StringIO()
            with patch.object(check_contact_info, "ROOT", root), patch("sys.argv", ["checker", "--site-dir", str(root)]):
                with redirect_stderr(output), redirect_stdout(output):
                    status = check_contact_info.main()
            self.assertEqual(status, 1)
            self.assertIn("cv-missing.pdf", output.getvalue())
            self.assertIn("missing or invalid artifact", output.getvalue())


if __name__ == "__main__":
    unittest.main()
