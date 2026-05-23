# Role-targeted LaTeX CVs

Source for the polished PDF resumes downloaded from
[cnpcshangbo.github.io/resumes/](https://cnpcshangbo.github.io/resumes/).

- `cv-robotics.tex` — Robotics Software Engineer view. Built to `/assets/cv-robotics.pdf`.
- `cv-ml.tex` — Machine Learning Engineer view. Built to `/assets/cv-ml.pdf`.

These are written in resume style (concise, action-verb bullets) and are
distinct from the longer-form narrative on the corresponding `/cv/robotics/`
and `/cv/ml/` web pages. The full academic CV at `/cv/` and its `cv.pdf`
remain hand-curated separately.

## Building locally

```
latexmk -pdf cv-robotics.tex
latexmk -pdf cv-ml.tex
```

Requires a TeX Live distribution with `latex-recommended`, `latex-extra`, and
`fonts-recommended` packages.

## CI

`.github/workflows/generate-cv-pdfs.yml` rebuilds both PDFs when any file
under `cv-tex/` changes (or via manual workflow_dispatch) and commits the
output to `assets/cv-robotics.pdf` and `assets/cv-ml.pdf`, then triggers a
GitHub Pages rebuild so the new downloads go live.

Template adapted from
[Sourabh Bajaj's resume template](https://github.com/sb2nov/resume) (MIT).
