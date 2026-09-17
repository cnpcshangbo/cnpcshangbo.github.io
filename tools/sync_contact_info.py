#!/usr/bin/env python3
"""Generate the shared LaTeX contact field from the website's author.email."""

from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    config = yaml.safe_load((ROOT / "_config.yml").read_text())
    email = config["author"]["email"]
    # Keep the generated TeX safe and predictable. Extend escaping explicitly
    # if a future address requires TeX-special characters.
    if not isinstance(email, str) or not re.fullmatch(r"[A-Za-z0-9.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email):
        raise SystemExit("author.email must be a valid address without TeX-special characters")
    target = ROOT / "cv-tex/contact-info.tex"
    target.write_text(
        "% Generated from _config.yml author.email; do not edit.\n"
        f"\\newcommand{{\\cvemail}}{{{email}}}\n"
    )
    print(f"Generated {target.relative_to(ROOT)} from author.email ({email})")


if __name__ == "__main__":
    main()
