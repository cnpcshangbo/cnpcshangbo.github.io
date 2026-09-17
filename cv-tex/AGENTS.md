# Public CV and contact maintenance

- `_config.yml` `author.email` is the canonical public contact address. Use `site.author.email` in pages and the generated `cv-tex/contact-info.tex` macro in LaTeX resumes.
- After contact changes, run `python tools/sync_contact_info.py`, rebuild the role PDFs, and run `python tools/build_academic_cv.py`. The academic PDF and web CV come from `_data/cv.yml`, `_data/publications.yml`, and the canonical contact config. Do not edit generated `_pages/cv.md` or `assets/cv.pdf` by hand.
- Before publishing, install `tools/requirements-academic-cv.txt` and run `python tools/check_contact_info.py`. After the Jekyll build, run it with `--site-dir _site`; after deployment, use `--live-base-url https://cnpcshangbo.github.io`.
- Do not treat a successful HTTP download as proof of correct PDF contents. Check all CV PDFs, including newly added variants. See `cv-tex/README.md` for the complete update procedure.
- Run `python tools/build_academic_cv.py --check` before publication; changes to appointments, projects, or bibliography must appear in both academic outputs. Regenerate rather than bypassing the consistency check.
