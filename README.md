# Highly Aligned Therapy — rebuilt site

Static HTML/CSS/JS. No framework, no build step needed to *run* it.

```
index.html              Home (About lives here as the "Learn More about me" accordion → /#about)
services/index.html     Services: Therapy, Reiki (coming soon), Qualified Supervision (coming soon)
consultation/index.html Consultation Inquiry form (+ Grow Therapy booking card)
about/ therapy/ reiki/ supervision/ home/   old Squarespace URLs → redirect to the new places
assets/                 css, js, fonts (self-hosted Syne + Syne Mono), img
```

## Preview locally
```bash
python3 -m http.server 4173
```
Open http://localhost:4173. (Use a server — links are root-relative, so opening the files directly won't work.)

## Deploy
Publish everything **except** `_audit/`, `_tools/`, `.claude/` to any static host (Netlify, Cloudflare Pages, Vercel, GitHub Pages…).

## Inquiry form → email
The form posts to FormSubmit (formsubmit.co) which emails each inquiry to pmh@highlyalignedtherapy.com
(`inquiry-endpoint` meta tag in `consultation/index.html`, set in `_tools/build.py` as `endpoint_meta`).
**One-time activation:** the first submission sends Paige an activation email — she must click it, or inquiries are not delivered.
After activating, FormSubmit gives her a random alias; swap it into the endpoint URL so her address isn't visible in the page source.
Note: this is a third-party relay — don't put clinical details in the form, and consider a HIPAA-compliant form service if she wants
inquiries to carry health information.

## Editing
`_tools/build.py` generates the three pages **and pulls all original copy from `_audit/extracted/`** so the text stays 1:1.
Re-running it overwrites the HTML, so make content/layout edits there (or stop using it and hand-edit the HTML).

```bash
python3 -I _tools/build.py     # regenerate pages
python3 -I _tools/verify.py    # text 1:1 vs. original, images, Grow links
```
`verify.py` also prints every piece of text that was *added* to the original (labels, tags, helper text).

## Booking funnel
All "Inquire" buttons and the top bar ("Now accepting new clients · Inquire →") go to `/consultation/`, which now asks
"Insurance or private pay?". Grow and Headway links appear **only** on the matching insurance cards on the Services page;
the private-pay card goes to the inquiry form.

## Swapping photos on the /alt/ About cards
Edit `ABOUT_CARD_VISUALS` in `_tools/build.py` (one entry per card; `kind` is `photo` = arch frame + warm grade + grain,
`tile` = full-bleed brand tile, `shape` = brand shape on a colour). Drop the new file in `assets/img/`, then re-run `build.py`.
A real portrait or lifestyle photo works best as `kind="photo"`.

## Not carried over (on purpose)
- Store, Cart (empty), Privacy Policy and Terms & Conditions — the last two are untouched Squarespace template filler ("It all begins with an idea…"), not real policies, and nothing linked to them. A therapy practice should publish real ones.
- `/book-session` — an unlinked Acuity scheduler page ("work with me / 1x1 private sessions, monthly mentorship").
