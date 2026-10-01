# CV maintenance

The site has two public documents: a two-page **Research Scientist Resume**
(`/cv/research/`) and the complete **Academic CV** (`/cv/`).

## Research Scientist resume

Edit `_data/research_resume.yml` for the research summary, selected experience,
research contributions, publication selections, and technical expertise. The
builder resolves appointment titles, institutions, dates, and education from
`_data/cv.yml`, publications from `_data/publications.yml`, and contact details
from `_config.yml`. Selection references must match exactly one canonical entry;
an absent or ambiguous reference fails rather than guessing.

```sh
python -m pip install -r tools/requirements-academic-cv.txt
python tools/build_research_resume.py
python tools/build_research_resume.py --check
```

This writes `_pages/cv-research.md` and `assets/cv-research-scientist.pdf`.
The first page contains the profile, selected research experience, and education;
the second starts with selected research, followed by publications and expertise.
The builder rejects overflow beyond two pages instead of reducing the font.
Review the rendered PDF after content edits. Commit shared data and both generated
outputs together. The check compares readable text, page boundaries, hyperlinks,
and a source fingerprint that includes the renderer and dependency pins.

The old role download filenames (`cv-fde.pdf`, `cv-robotics.pdf`, `cv-ml.pdf`,
`cv-applied-ai.pdf`, and `cv-solutions-engineer.pdf`) are compatibility aliases:
the builder copies the same research resume bytes to all five and checks that
they remain identical. They do not represent separate public resume versions.

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

## Historical role sources and contact changes

The LaTeX files under `cv-tex/` are historical tailored sources retained for
reference. They are excluded from the website and are no longer built by CI or
authoritative for public downloads. The previous role PDFs and their sources
were also archived locally before consolidation. Do not copy a historical role
build over the public PDF aliases.

After changing `_config.yml` `author.email`:

```sh
python tools/sync_contact_info.py
python tools/build_research_resume.py
python tools/build_academic_cv.py
python tools/check_contact_info.py
```

Both public PDFs use ReportLab and do not require LaTeX. The generated contact
include is retained so historical sources still use the canonical email.

## Build and deployment checks

`generate-cv-pdfs.yml` rebuilds the research resume, its compatibility aliases,
and the academic CV when CV data, bibliography, contact config, or build tooling change.
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
It checks `/cv/research/` and follows static redirects from the old resume pages
to validate the destination's contact links.
Do not switch Pages to branch-based publishing, which bypasses these gates.

| Source | Download |
| --- | --- |
| `_data/research_resume.yml` + shared CV/bibliography/config | `/assets/cv-research-scientist.pdf` |
| `_data/cv.yml` + `_data/publications.yml` | `/assets/cv.pdf` |
| Exact copies of the research resume | All five historical `/assets/cv-<role>.pdf` URLs |

Role template adapted from
[Sourabh Bajaj's resume template](https://github.com/sb2nov/resume) (MIT).
