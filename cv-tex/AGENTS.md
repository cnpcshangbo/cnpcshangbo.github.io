# Public CV and contact maintenance

- `_config.yml` `author.email` is the canonical public contact address. Use `site.author.email` in pages and the generated `cv-tex/contact-info.tex` macro in LaTeX resumes.
- After contact changes, run `python tools/sync_contact_info.py`, rebuild the role PDFs, and update the separately maintained academic `assets/cv.pdf`. Its visible text AND clickable `mailto:` link must match the canonical address.
- Before publishing, install `tools/requirements-contact.txt` and run `python tools/check_contact_info.py`. After the Jekyll build, run it with `--site-dir _site`; after deployment, use `--live-base-url https://cnpcshangbo.github.io`.
- Do not treat a successful HTTP download as proof of correct PDF contents. Check all CV PDFs, including newly added variants. See `cv-tex/README.md` for the complete update procedure.

