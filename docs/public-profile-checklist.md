# Public profile update checklist

Use this checklist whenever an appointment, title, or public contact address
changes. It is a reusable checklist, not a record that every platform is current.

## Confirm the source facts

Update the source records first. The baseline confirmed on 2026-09-17 is:

- Current institution: **University of Maryland, College Park**.
- Current role: **Postdoctoral Associate**, Civil and Environmental Engineering /
  Maryland Transportation Institute, **2026-07 to present**.
- Most recent CUNY / City College appointment: **2025-07 to 2026-06**.
- Public contact email: **bshang@umd.edu**.

The website's authoritative records are [`_data/cv.yml`](../_data/cv.yml)
for appointments and [`_config.yml`](../_config.yml) `author.email` for the
public email. Reconfirm these facts when the next change occurs; update this
dated baseline too. Preserve earlier appointments and affiliations printed on
historical publications. Do not infer a move of home address from a job change.

## Update and verify every destination

For each row: confirm the signed-in identity, inspect current public fields,
save applicable changes, then reload the public profile. Check both current
institution/title and the previous appointment's end date. Where public email
or an institutional verification domain is displayed, confirm it is current;
record any pending verification separately. Account login and recovery emails
are separate from public contact information.

| Destination | Fields and outputs to inspect |
| --- | --- |
| [Website](https://cnpcshangbo.github.io/) and [CV](https://cnpcshangbo.github.io/cv/) | Bio/sidebar, academic web CV, [resume index](https://cnpcshangbo.github.io/resumes/), both role web timelines, all six downloadable CV PDFs |
| [LinkedIn](https://www.linkedin.com/in/bo-shang/) | Headline, About, current UMD experience, CUNY end date, public contact information |
| [ORCID](https://orcid.org/0000-0002-5568-1566) | Employment records and dates, visibility, biography, public researcher links/email |
| [Web of Science](https://www.webofscience.com/wos/author/record/38030) | Editable profile affiliation and institution history; distinguish publication-derived affiliations |
| [ResearchGate](https://www.researchgate.net/profile/Bo-Shang) | Current institution/department/position, previous affiliations and end dates, introduction |
| [Facebook](https://www.facebook.com/cnpcshangbo) | Public Intro/About and Work records; preserve audience settings and avoid creating a separate announcement |
| [GitHub](https://github.com/cnpcshangbo) | Bio and any existing public company/contact fields |
| [Google Scholar](https://scholar.google.com/citations?user=TVIPpDMAAAAJ&hl=en) | Profile affiliation, verified email domain, homepage link |

Keep a per-update record with **URL, changed fields, checked date, and result**
(`verified`, `already current`, or a specific blocker/pending verification).
Search excerpts can lag behind saved profiles; they are not proof of a live
update. Do not mark a platform complete until the saved destination is checked.

## Website and PDF completion gate

- [ ] Update shared academic records, relevant `_pages/` bios/timelines, and all
  five `cv-tex/cv-*.tex` role appointment entries. Audit project date ranges when
  they describe the same appointment; keep unrelated historical dates intact.
- [ ] Follow the [CV build procedure](../cv-tex/README.md): sync contact data,
  rebuild all role PDFs, and regenerate the academic web CV and PDF. Never edit
  generated `_pages/cv.md` or `assets/cv.pdf` by hand.
- [ ] Run `python tools/build_academic_cv.py --check` and
  `python tools/check_contact_info.py`; inspect actual PDF dates and rendered
  pages. Contact validation alone does not validate appointment dates.
- [ ] Confirm the final PDF-generation and website-deployment workflows pass.
  Run `python tools/check_contact_info.py --live-base-url https://cnpcshangbo.github.io`
  and reopen the live pages and every linked PDF to verify the new dates,
  institution, and email. Refresh any separately delivered local CV copy.
