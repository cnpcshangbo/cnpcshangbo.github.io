# CV PDFs and contact information

The public email has one source of truth: `_config.yml` → `author.email`.
Jekyll pages use `site.author.email`. All five role resumes include
`contact-info.tex` and use `\cvemail` for both the visible address and mailto
link. Generate that include with `python tools/sync_contact_info.py`; do not
edit it directly.

## Updating contact information

1. Change `author.email` in `_config.yml`.
2. Install the checker dependencies and generate the shared LaTeX field:

   ```sh
   python -m pip install -r tools/requirements-contact.txt
   python tools/sync_contact_info.py
   ```

3. Rebuild all role resumes from the `cv-tex` directory (requires TeX Live
   with latex-extra and fonts-recommended, plus latexmk):

   ```sh
   cd cv-tex
   for role in robotics ml fde applied-ai solutions-engineer; do
     latexmk -pdf -interaction=nonstopmode -halt-on-error "cv-$role.tex"
     cp "cv-$role.pdf" "../assets/cv-$role.pdf"
   done
   cd ..
   ```

4. Update `assets/cv.pdf`, the separately maintained full academic CV.
   The original editable source for this PDF is not stored here. Updating
   the web page or role LaTeX sources does **not** update this file. Check
   both its visible email and clickable email link, then review rendering.
   Preserve historical affiliations and research content unless those
   changes are also being intentionally reviewed.
5. Validate the committed files and rendered website:

   ```sh
   python tools/check_contact_info.py
   bundle exec jekyll build --destination _site
   python tools/check_contact_info.py --site-dir _site
   ```

6. Commit the config, generated include, and updated PDFs together. After
   Pages finishes deploying, verify the actual public downloads:

   ```sh
   python tools/check_contact_info.py --live-base-url https://cnpcshangbo.github.io
   ```

The checker reads actual PDF text and annotation links; it is not an HTTP
availability check. It discovers `assets/cv*.pdf` and additional linked CV
downloads, so new variants are included. Missing files, missing contact
fields, and conflicting addresses fail the check.

## Automation

`generate-cv-pdfs.yml` regenerates the shared contact include and all five
role PDFs when the config, LaTeX, or contact tooling changes. It validates
**all** CVs, including the academic PDF, before committing generated files.
An old academic CV must be corrected before that workflow can succeed.

`check-pages.yml` checks source assets and the built site on updates and
pull requests, then checks live pages and downloads after deployment and
every Monday. A failed check requires correction; it is not an automatic
repair of an uploaded academic PDF.

`deploy-pages.yml` is the only Pages publication path (repository Pages
source: GitHub Actions). It requires source/PDF checks and checks of the
exact generated website artifact before deployment, then validates public
URLs after deployment. A contact mismatch stops publication, leaving the
previous successful site live. Do not switch Pages back to branch-based
publishing, which bypasses these checks.

The concise role PDFs are separate from the longer-form web CV pages:

| Source | Download |
| --- | --- |
| `cv-robotics.tex` | `/assets/cv-robotics.pdf` |
| `cv-ml.tex` | `/assets/cv-ml.pdf` |
| `cv-fde.tex` | `/assets/cv-fde.pdf` |
| `cv-applied-ai.tex` | `/assets/cv-applied-ai.pdf` |
| `cv-solutions-engineer.tex` | `/assets/cv-solutions-engineer.pdf` |
| Separately maintained academic CV | `/assets/cv.pdf` |

Role template adapted from
[Sourabh Bajaj's resume template](https://github.com/sb2nov/resume) (MIT).
