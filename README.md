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

## ⚠️ The inquiry form needs a destination
Squarespace's form backend doesn't come with the content, so the form currently has nowhere to send.
Until it's connected it tells visitors so (and points them to Grow Therapy) rather than pretending to send.

1. Create a form endpoint (e.g. a free Formspree form pointed at Paige's email).
2. Put its URL in `_tools/build.py` (`endpoint_meta`, the `inquiry-endpoint` meta tag) and run `python3 -I _tools/build.py` —
   or edit the `<meta name="inquiry-endpoint" content="">` line directly in `consultation/index.html`.

The form posts `first, last, email, day, message, time, phone` (+ `preferred_time_readable`) as form data with `Accept: application/json`.
There's a hidden honeypot field for spam; add the service's own CAPTCHA if you want one like Squarespace had.

## Editing
`_tools/build.py` generates the three pages **and pulls all original copy from `_audit/extracted/`** so the text stays 1:1.
Re-running it overwrites the HTML, so make content/layout edits there (or stop using it and hand-edit the HTML).

```bash
python3 -I _tools/build.py     # regenerate pages
python3 -I _tools/verify.py    # text 1:1 vs. original, images, Grow links
```
`verify.py` also prints every piece of text that was *added* to the original (labels, tags, helper text).

## Not carried over (on purpose)
- Store, Cart (empty), Privacy Policy and Terms & Conditions — the last two are untouched Squarespace template filler ("It all begins with an idea…"), not real policies, and nothing linked to them. A therapy practice should publish real ones.
- `/book-session` — an unlinked Acuity scheduler page ("work with me / 1x1 private sessions, monthly mentorship").
