# CV maintenance

The public academic CV has three shared inputs:

- `_data/cv.yml`: profile, appointments, education, projects, teaching, service,
  honors, and technical expertise.
- `_data/publications.yml`: bibliography shared with `/publications/`, including
  publication types and direct source links. Keep preprints, conference papers,
  journal articles, patents/applications, reports, and presentations distinct.
- `_config.yml` `author.email` and profile links: canonical public contact.

## Academic CV: one update, two outputs

```sh
python -m pip install -r tools/requirements-academic-cv.txt
python tools/build_academic_cv.py
python tools/build_academic_cv.py --check
python tools/check_contact_info.py
```

The builder writes `_pages/cv.md` and `assets/cv.pdf`. Both have the same
review date, content, and bibliography. Edit the data rather than either
output; commit inputs and generated outputs together. Update `cv.yml`'s
`updated` field when reviewing substantive CV changes.

The check regenerates expected content and checks the committed web page,
PDF content, PDF links, and source fingerprint. A forgotten or manually
replaced PDF fails publication. Render the PDF and review all pages after
substantive changes; automated consistency checks cannot judge typography
or verify the truth of a newly entered career claim.

The bibliography drives the Publications page too. Its citation counts retain
an explicit dated Google Scholar snapshot; bibliographic review is tracked
separately and does not imply refreshed citation counts.

## Role resumes and email changes

Role resumes remain concise, tailored LaTeX documents under `cv-tex/`.
Every role includes generated `contact-info.tex` and uses `\cvemail` for
visible text and mailto. After changing `_config.yml` `author.email`:

```sh
python tools/sync_contact_info.py
python tools/build_academic_cv.py
cd cv-tex
for role in robotics ml fde applied-ai solutions-engineer; do
  latexmk -pdf -interaction=nonstopmode -halt-on-error "cv-$role.tex"
  cp "cv-$role.pdf" "../assets/cv-$role.pdf"
done
cd ..
python tools/check_contact_info.py
```

Role builds require TeX Live with latex-extra/fonts-recommended and latexmk.
The academic PDF uses ReportLab and does not require LaTeX.

## Build and deployment checks

`generate-cv-pdfs.yml` rebuilds the academic CV and all five role PDFs when
CV data, bibliography, contact config, sources, or build tooling change.
It validates the outputs, commits them together, and explicitly dispatches
`deploy-pages.yml` for bot-generated commits.

`deploy-pages.yml` is the only Pages publication path (repository Pages
source: GitHub Actions). It checks source/output consistency, builds Jekyll,
and validates the exact artifact before deployment. A mismatch leaves the
previous successful site online. It then checks public contact details.
`check-pages.yml` also runs on updates/PRs and checks public URLs every Monday.

```sh
bundle exec jekyll build --destination _site
python tools/check_contact_info.py --site-dir _site
python tools/check_contact_info.py --live-base-url https://cnpcshangbo.github.io
```

The contact checker validates every `assets/cv*.pdf` and additional linked
CV downloads, including actual PDF text and clickable mailto targets.
Do not switch Pages to branch-based publishing, which bypasses these gates.

| Source | Download |
| --- | --- |
| `_data/cv.yml` + `_data/publications.yml` | `/assets/cv.pdf` |
| `cv-robotics.tex` | `/assets/cv-robotics.pdf` |
| `cv-ml.tex` | `/assets/cv-ml.pdf` |
| `cv-fde.tex` | `/assets/cv-fde.pdf` |
| `cv-applied-ai.tex` | `/assets/cv-applied-ai.pdf` |
| `cv-solutions-engineer.tex` | `/assets/cv-solutions-engineer.pdf` |

Role template adapted from
[Sourabh Bajaj's resume template](https://github.com/sb2nov/resume) (MIT).
