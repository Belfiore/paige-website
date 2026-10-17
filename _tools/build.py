#!/usr/bin/env python3
"""Generate the static site from the audited original copy.

Every visible string of original copy is pulled from _audit/extracted/*.json
(the programmatic crawl of highlyalignedtherapy.com), never retyped, so the
text stays 1:1. Only labels, tags, helper text and a11y strings are authored
here (listed in ADDED_TEXT below, and echoed by verify.py).

Run:  python3 -I _tools/build.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "_audit", "extracted")

_cache = {}


def _page(name):
    if name not in _cache:
        with open(os.path.join(EX, name + ".json"), encoding="utf-8") as f:
            _cache[name] = json.load(f)
    return _cache[name]


def clean(t):
    t = t.replace("‍", "").replace(" ", " ")
    return re.sub(r"\s+", " ", t).strip()


def lines(page, regions=("main", "footer")):
    return [clean(l["text"]) for l in _page(page)["lines"] if l["region"] in regions and clean(l["text"])]


def X(page, text, regions=("main", "footer")):
    """Exact line must exist on the original page; return it."""
    assert text in lines(page, regions), f"{page}: exact line not found: {text!r}"
    return text


def T(page, start, regions=("main", "footer")):
    """Full original line that starts with `start` (must be unique)."""
    m = [l for l in lines(page, regions) if l.startswith(start)]
    assert len(m) == 1, f"{page}: {len(m)} lines start with {start!r}"
    return m[0]


def E(t):
    return html.escape(t, quote=False)


def A(t):
    return html.escape(t, quote=True)


def sentences(t, n):
    parts = re.split(r"(?<=[.!?])\s+", t)
    return " ".join(parts[:n])


def link(page, text):
    for l in _page(page)["links"]:
        if clean(l["text"]) == text:
            return l["href"]
    raise AssertionError(f"{page}: link not found: {text!r}")


# ---- Destinations (all taken from the original site) ---------------------
GROW = next(l["href"] for l in _page("root")["links"] if l["href"].startswith("https://growtherapy.com/book-appointment"))
assert GROW == "https://growtherapy.com/book-appointment?prsid=oq1cmlyoxaaf&ref=grow&setting=Virtual&insuranceId=&state=&cusid="
PAY_GROW = link("therapy", "Book Session")
PAY_HEADWAY = link("therapy", "Book with Aetna or Cigna")
PAY_FLBLUE = link("therapy", "Book with Florida Blue or United")

EXT = '<svg class="ext" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M6 3h7v7M13 3 4 12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CHEV = '<svg viewBox="0 0 12 12" aria-hidden="true" focusable="false"><path d="m2 4 4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
NEWTAB = '<span class="visually-hidden"> (opens in a new tab)</span>'
STARS = '<div class="star-row" aria-hidden="true">' + "<i></i>" * 11 + "</div>"


ARR_BTN = '<svg class="ext" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M2 8h11M9 3.5 13.5 8 9 12.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def inquire_btn(label="Inquire", extra_cls="btn--solid"):
    """Primary CTA: goes to the inquiry form (consultation first, private-pay friendly)."""
    return f'<a class="btn {extra_cls}" href="/consultation/"><span>{E(label)}</span>{ARR_BTN}</a>'


def grow_btn(label, extra_cls="btn--solid"):
    return (f'<a class="btn {extra_cls}" data-grow href="{A(GROW)}" target="_blank" rel="noopener noreferrer">'
            f'<span>{E(label)}</span>{EXT}{NEWTAB}</a>')


# ---- Shared chrome ---------------------------------------------------------
HEAD_SCRIPT = ("(function(d){d.classList.add('js');try{if(!sessionStorage.getItem('hat-intro')&&"
               "!matchMedia('(prefers-reduced-motion: reduce)').matches){d.classList.add('intro-pending');"
               "setTimeout(function(){d.classList.remove('intro-pending')},7000)}}catch(e){}})(document.documentElement)")


def head(title, desc, extra=""):
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{A(desc)}">
<meta name="theme-color" content="#F6F3EC">
<meta property="og:site_name" content="Highly Aligned Therapy">
<meta property="og:title" content="{A(title)}">
<meta property="og:description" content="{A(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://www.highlyalignedtherapy.com/assets/img/logo-512.png">
<link rel="icon" type="image/png" href="/assets/img/favicon.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/syne-latin.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/syne-mono-latin.woff2" crossorigin>
<script>{HEAD_SCRIPT}</script>
<link rel="stylesheet" href="/assets/css/styles.css">
{extra}</head>
"""


INTRO = """<div id="intro" aria-hidden="true">
  <div class="intro-stage">
    <div class="intro-orbit"></div>
    <img class="intro-logo" src="/assets/img/logo-512.png" alt="" width="512" height="512">
  </div>
  <p class="intro-skip">Tap to skip</p>
</div>
"""


def header(current=None, home="/"):
    lab = lambda s: E(X("root", s, ("header",)))
    svc_cur = ' aria-current="page"' if current == "services" else ""
    home_cur = ' aria-current="page"' if current == "home" else ""
    return f"""<div class="announce" role="region" aria-label="Booking announcement"><span class="pulse-dot" aria-hidden="true"></span><span>Now accepting new clients</span>
  <a href="/consultation/">Inquire →</a></div>
<header class="site-header">
  <a class="skip" href="#main">{lab("Skip to Content")}</a>
  <div class="header-inner">
    <a class="brand" href="{home}"><img src="/assets/img/logo-320.webp" width="62" height="62" alt="Highly Aligned Therapy"></a>
    <nav class="primary-nav" id="primary-nav" aria-label="Primary">
      <ul>
        <li><a class="nav-link" href="{home}"{home_cur}>Home</a></li>
        <li><a class="nav-link" href="/services/"{svc_cur}>{lab("Services")}</a></li>
        <li><a class="nav-link" href="{home}#about" data-open-about>{lab("About")}</a></li>
        <li><a class="nav-link" href="/consultation/"{' aria-current="page"' if current == "consult" else ""}>{E(X("root", "WORK WITH ME"))}</a></li>
      </ul>
      <div class="nav-cta-mobile">{inquire_btn()}</div>
    </nav>
    {inquire_btn().replace('class="btn btn--solid"', 'class="btn btn--solid header-cta"')}
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="primary-nav"><span class="bars" aria-hidden="true"></span><span class="menu-label">Open Menu</span></button>
  </div>
</header>
"""


def footer(extra_li="", home="/"):
    return f"""<footer class="site-footer">
  <div class="wrap">
    <a href="/" aria-label="Highly Aligned Therapy — home"><img class="logo-lg" src="/assets/img/logo-512.png" width="184" height="184" alt="" loading="lazy"></a>
    <ul class="footer-links">
      <li><a href="{home}#about" data-open-about>{E(X("root", "ABOUT"))}</a></li>
      <li><a href="/consultation/">{E(X("root", "WORK WITH ME"))}</a></li>{extra_li}
    </ul>
  </div>
</footer>
<script src="/assets/js/main.js" defer></script>
</body>
</html>
"""


def soon_title(full):
    """'Reiki Services — Coming Soon' -> title + visually-hidden dash + tag, text stays 1:1."""
    m = re.match(r"^(.*?) — (Coming Soon)$", full)
    assert m, full
    return f'{E(m.group(1))} <span class="visually-hidden">—</span> <span class="tag tag--soon">{E(m.group(2))}</span>'


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------
def home():
    p = "root"
    meet_p1 = T(p, "Greetings!")
    desc = meet_p1.split(" :)")[0].replace("Greetings! ", "", 1)
    therapy_intro = T("therapy", "I believe the therapeutic relationship")
    reiki_p = T("reiki", "This offering is still")
    sup_p = T("supervision", "Qualified supervision services")
    about_ps = [T("about", s) for s in ("I became a therapist", "I believe that understanding", "I consider myself")]

    steps = [("icon-awaken", "AWAKEN"), ("icon-attune", "ATTUNE"), ("icon-align", "ALIGN")]
    steps_html = "\n".join(
        f"""        <article class="step" data-reveal style="--delay:{i*0.12:.2f}s">
          <img src="/assets/img/{img}.webp" alt="" width="72" height="72" loading="lazy">
          <h3>{E(X(p, h))}</h3>
          <p>{E(T(p, {'AWAKEN': 'Explore the experiences', 'ATTUNE': 'Develop a deeper', 'ALIGN': 'Turn self-awareness'}[h]))}</p>
        </article>""" for i, (img, h) in enumerate(steps))

    tiles = [("tile-sunburst", ""), ("tile-mandala-warm", "Crystal mandala in warm tones"), ("tile-ring", ""),
             ("tile-flower", ""), ("tile-mandala-blue", "Crystal mandala in blue tones")]
    tiles_html = "\n".join(
        f'          <li><img src="/assets/img/{n}.webp" alt="{A(a)}" width="900" height="900" loading="lazy"></li>' for n, a in tiles)

    return head("Highly Aligned Therapy", desc) + f"""<body class="has-announce page-home">
{INTRO}{header("home", "/classic/")}
<main id="main">

  <div class="hero-wrap">
    <div class="hero-media" aria-hidden="true"></div>
    <section class="hero" aria-labelledby="hero-title">
      <div class="sparkles" data-sparkles="18" aria-hidden="true"></div>
      <div class="wrap">
        <h1 id="hero-title" data-split>{E(T(p, "come as you are"))}</h1>
        <div class="paper-card hero-card" data-reveal>
          <p>{E(T(p, "You don’t need to have everything"))}</p>
          <p>{E(T(p, "If your own mind"))}</p>
        </div>
      </div>
    </section>
    <section class="hero-2" aria-label="Leave as yourself">
      <div class="wrap"><h2 data-split>{E(T(p, ". . .Leave as Yourself"))}</h2></div>
    </section>
  </div>

  <section class="section meet" id="about" aria-labelledby="meet-title">
    <div class="sparkles" data-sparkles="9" aria-hidden="true"></div>
    <div class="wrap">
      <div class="meet-grid">
        <div class="portrait" data-reveal>
          <img src="/assets/img/paige-portrait.webp" width="1085" height="1450" alt="Paige Haile, smiling, outdoors" loading="lazy">
        </div>
        <div class="meet-text" data-reveal style="--delay:.12s">
          <h2 id="meet-title">{E(X(p, "meet Paige"))}</h2>
          <p>{E(meet_p1)}</p>
          <p>{E(T(p, "I blend evidence-based tools"))}</p>
          <button class="acc-trigger" id="about-trigger" type="button" aria-expanded="false" aria-controls="about-panel"><span>{E(X(p, "Learn More"))}</span> <span class="acc-sub">about me</span><span class="acc-icon" aria-hidden="true"></span></button>
        </div>
      </div>

      <div class="acc-panel" id="about-panel" role="region" aria-labelledby="about-trigger">
        <div class="acc-inner">
          <div class="about-body stagger">
            <h3 class="about-title" style="--k:0">{E(T("about", "ABOUT paige"))}</h3>
            <div class="about-grid" style="--k:1">
              <div class="about-photo">
                <img src="/assets/img/about-sunset.webp" width="1206" height="1278" alt="Paige on a Gulf-coast beach at sunset, arms raised" loading="lazy">
                <img class="bloom" src="/assets/img/bloom-blue.webp" alt="" width="282" height="166" loading="lazy">
              </div>
              <div class="about-text">
                <p>{E(about_ps[0])}</p>
                <p>{E(about_ps[1])}</p>
                <p>{E(about_ps[2])}</p>
              </div>
            </div>
            <ul class="tiles" style="--k:2">
{tiles_html}
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section quote" aria-label="Quote">
    <div class="wrap">
      <figure class="paper-card" data-reveal>
        <img class="bloom" src="/assets/img/bloom-blue.webp" alt="" width="282" height="166" loading="lazy">
        <blockquote><p>{E(T(p, "“One does not become"))}</p></blockquote>
        {STARS}
        <figcaption>{E(T(p, "— Carl Jung"))}</figcaption>
      </figure>
    </div>
  </section>

  <section class="section journey" aria-labelledby="journey-title">
    <div class="wrap">
      <div class="journey-title" data-reveal>
        <h2 id="journey-title">{E(X(p, "The Journey"))}</h2>
        {STARS}
      </div>
      <div class="journey-grid">
{steps_html}
      </div>
    </div>
    <button class="pause-btn" type="button" aria-pressed="false" aria-label="Pause background animation">
      <svg class="i-pause" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1.5v11M11 1.5v11" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>
      <svg class="i-play" viewBox="0 0 14 14" aria-hidden="true"><path d="M3.5 1.8v10.4L12 7z" fill="currentColor"/></svg>
    </button>
  </section>

  <section class="section teasers" id="services-preview" aria-labelledby="teasers-title">
    <div class="wrap">
      <div class="teasers-head" data-reveal>
        <h2 id="teasers-title">Services</h2>
        <a class="link-arrow" href="/services/">See all services {ARROW}</a>
      </div>
      <div class="teaser-grid">
        <article class="teaser teaser--main" data-reveal>
          <div><span class="tag">Available now</span></div>
          <h3>{E(X(p, "Therapy", ("header",)))}</h3>
          <p>{E(sentences(therapy_intro, 2))}</p>
          <div class="teaser-links">
            {inquire_btn()}
            <a class="link-arrow" href="/services/#therapy">{E(X(p, "Learn more"))} {ARROW}</a>
          </div>
        </article>
        <article class="teaser teaser--soon" data-reveal style="--delay:.1s">
          <h3>{soon_title(T("reiki", "Reiki Services"))}</h3>
          <p>{E(sentences(reiki_p, 2))}</p>
          <div class="teaser-links"><a class="link-arrow" href="/services/#reiki">{E(X(p, "Learn more"))} {ARROW}</a></div>
        </article>
        <article class="teaser teaser--soon" data-reveal style="--delay:.2s">
          <h3>{soon_title(T("supervision", "Qualified Supervision"))}</h3>
          <p>{E(sentences(sup_p, 2))}</p>
          <div class="teaser-links"><a class="link-arrow" href="/services/#supervision">{E(X(p, "Learn more"))} {ARROW}</a></div>
        </article>
      </div>
    </div>
  </section>

  <section class="section closing" aria-labelledby="closing-title">
    <div class="sparkles" data-sparkles="10" aria-hidden="true"></div>
    <div class="wrap">
      <h2 id="closing-title" data-reveal>{E(X(p, "Lets Align."))}</h2>
      <div class="cta-row" data-reveal style="--delay:.1s">
        <a class="btn" href="/services/#therapy">{E(X(p, "Learn more"))}</a>
        {inquire_btn()}
      </div>
      <p class="btn-note" style="margin-inline:auto">Share a few details and I’ll be in touch.</p>
    </div>
  </section>

</main>
""" + footer('<li><a href="/">See the new home page</a></li>', "/classic/")


# ---------------------------------------------------------------------------
# SERVICES
# ---------------------------------------------------------------------------
def services():
    t = "therapy"
    r_title = T("reiki", "Reiki Services")
    s_title = T("supervision", "Qualified Supervision")
    cards = [
        ("private pay", "Therapy sessions are 60 minutes", "Inquire about private pay", "/consultation/"),
        ("Aetna & Cigna", "Use Headway", "Book with Aetna or Cigna", PAY_HEADWAY),
        ("Florida Blue & United Healthcare", "Use Grow Therapy", "Book with Florida Blue or United", PAY_FLBLUE),
    ]
    def pay_btn(t, b, url):
        if url.startswith("/"):   # private pay -> our own inquiry form
            return f'<a class="btn btn--solid" href="{A(url)}"><span>{E(b)}</span>{ARR_BTN}</a>'
        return f'<a class="btn" href="{A(url)}" target="_blank" rel="noopener noreferrer"><span>{E(X(t, b))}</span>{EXT}{NEWTAB}</a>'

    pay = "\n".join(f"""        <article class="pay-card" data-reveal style="--delay:{i*0.1:.1f}s">
          <h3>{E(X(t, h))}</h3>
          <p>{E(T(t, s))}</p>
          {pay_btn(t, b, url)}
        </article>""" for i, (h, s, b, url) in enumerate(cards))

    desc = sentences(T(t, "I believe the therapeutic relationship"), 1)
    return head("Services — Highly Aligned Therapy", desc) + f"""<body class="has-announce page-services">
{INTRO}{header("services")}
<main id="main">

  <section class="page-hero" aria-labelledby="services-title">
    <div class="sparkles" data-sparkles="10" aria-hidden="true"></div>
    <div class="wrap">
      <h1 id="services-title" data-split>Services</h1>
    </div>
  </section>

  <nav class="service-tabs" aria-label="Jump to a service">
    <ul>
      <li><a href="#therapy" aria-current="true"><span class="dot" aria-hidden="true"></span>{E(X("root", "Therapy", ("header",)))}</a></li>
      <li><a href="#reiki"><span class="dot dot--soon" aria-hidden="true"></span>{E(X("root", "Reiki", ("header",)))}<span class="visually-hidden"> — coming soon</span></a></li>
      <li><a href="#supervision"><span class="dot dot--soon" aria-hidden="true"></span>{E(X("root", "Qualified Supervision", ("header",)))}<span class="visually-hidden"> — coming soon</span></a></li>
    </ul>
  </nav>

  <section class="service section" id="therapy" aria-labelledby="therapy-title" style="padding-top:clamp(24px,4vw,48px)">
    <div class="wrap">
      <div class="service-head" data-reveal>
        <p class="eyebrow" style="margin:0">{E(X("root", "Therapy", ("header",)))}</p>
        <span class="tag">Available now</span>
      </div>
      <div class="split">
        <div class="split-text" data-reveal>
          <h2 id="therapy-title">{E(T(t, "Let’s align"))}</h2>
          <p>{E(T(t, "I believe the therapeutic relationship"))}</p>
          <p>{E(T(t, "I structure therapy"))}</p>
        </div>
        <div class="split-media split-media--tall" data-reveal style="--delay:.1s">
          <img src="/assets/img/therapy-stones.webp" width="1667" height="2500" alt="A column of polished stones in warm neutral tones" loading="lazy">
        </div>
      </div>

      <div class="split split--flip frame">
        <div class="split-text" data-reveal>
          <h2>{E(T(t, "setting the frame"))}</h2>
          <p>{E(T(t, "Our first session"))}</p>
          <p>{E(T(t, "I often begin sessions"))}</p>
          <p>{E(T(t, "From there, we’ll allow"))}</p>
        </div>
        <div class="split-media split-media--tall" data-reveal style="--delay:.1s">
          <img src="/assets/img/therapy-minerals.webp" width="1300" height="1919" alt="A grid of raw crystals and mineral specimens on white" loading="lazy">
        </div>
      </div>

      <div class="service-cta" data-reveal>
        {inquire_btn()}
        <p class="btn-note">Share a few details and I’ll be in touch.</p>
      </div>
    </div>

    <div class="insurance">
      <div class="wrap">
        <p class="eyebrow" data-reveal>{E(X(t, "Insurance & Payment"))}</p>
        <div class="pay-grid">
{pay}
        </div>
      </div>
    </div>
  </section>

  <section class="service soon-block" id="reiki" aria-labelledby="reiki-title">
    <div class="wrap">
      <div class="soon-card" data-reveal>
        <img src="/assets/img/icon-awaken.webp" alt="" width="171" height="175" loading="lazy">
        <div>
          <h2 id="reiki-title">{soon_title(r_title)}</h2>
          <p>{E(T("reiki", "This offering is still"))}</p>
        </div>
      </div>
    </div>
  </section>

  <section class="service soon-block" id="supervision" aria-labelledby="supervision-title" style="padding-top:0">
    <div class="wrap">
      <div class="soon-card" data-reveal>
        <img src="/assets/img/icon-align.webp" alt="" width="150" height="151" loading="lazy">
        <div>
          <h2 id="supervision-title">{soon_title(s_title)}</h2>
          <p>{E(T("supervision", "Qualified supervision services"))}</p>
          <span class="pill">{E(X("supervision", "Check Back Soon"))}</span>
        </div>
      </div>
    </div>
  </section>

</main>
""" + footer()


# ---------------------------------------------------------------------------
# CONSULTATION (Consultation Inquiry form — fields from the original form block)
# ---------------------------------------------------------------------------
FORM_EX_PLACEHOLDERS = {"day": "Example: Tuesdays or Thursdays",
                        "message": "Tell me briefly what you’re looking for support with."}
THANKS = ["Thank you for reaching out. I look forward to speaking with you!", "-Paige"]
FORM_LABELS = ["Name", "First Name", "Last Name", "Email", "Preferred Day", "Short Message",
               "Preferred Time", "in Eastern Time", "Phone Number", "Send Inquiry"]


def consultation():
    # the visible labels were captured from the rendered form (get_page_text); (required) is original text
    req = '<span class="req">(required)</span>'
    endpoint_meta = ('<!-- Set content to your form service URL (e.g. https://formspree.io/f/xxxxxxxx). While it is empty the form tells\n'
                     '     visitors it is not connected, instead of pretending to send. -->\n'
                     '<meta name="inquiry-endpoint" content="">\n')
    return head(clean(_page("consultation")["lines"][0]["text"]), "Consultation Inquiry — send a message to Paige Haile, Florida Licensed Mental Health Counselor.", endpoint_meta) + f"""<body class="has-announce page-consultation">
{INTRO}{header("consult")}
<main id="main">
  <section class="consult" aria-labelledby="consult-title">
    <div class="sparkles" data-sparkles="9" aria-hidden="true"></div>
    <div class="wrap">
      <h1 id="consult-title" data-split>Consultation Inquiry</h1>
      <div class="consult-grid">

        <div class="book-card" data-reveal>
          <h2 id="book-title">Have insurance?</h2>
          <p>If you have Aetna, Cigna, Florida Blue or United Healthcare, you can also request a session straight from your insurer’s booking page.</p>
          <a class="btn" href="/services/#therapy"><span>See insurance options</span>{ARR_BTN}</a>
        </div>

        <div class="form-card" data-reveal style="--delay:.1s">
          <p class="form-intro">Prefer to write first? Fill this out and I’ll be in touch. Fields marked (required) must be completed.</p>
          <div class="form-alert" role="alert" tabindex="-1"></div>

          <form id="inquiry" novalidate aria-label="Consultation Inquiry" method="post" action="#">
            <fieldset class="field">
              <legend>{E(FORM_LABELS[0])}</legend>
              <div class="name-row">
                <div class="field">
                  <label class="sub-label" for="f-first">{E(FORM_LABELS[1])} {req}</label>
                  <input class="input" id="f-first" name="first" type="text" autocomplete="given-name" required data-validate aria-describedby="e-first" aria-invalid="false">
                  <p class="error" id="e-first"></p>
                </div>
                <div class="field">
                  <label class="sub-label" for="f-last">{E(FORM_LABELS[2])} {req}</label>
                  <input class="input" id="f-last" name="last" type="text" autocomplete="family-name" required data-validate aria-describedby="e-last" aria-invalid="false">
                  <p class="error" id="e-last"></p>
                </div>
              </div>
            </fieldset>

            <div class="field">
              <label for="f-email">{E(FORM_LABELS[3])} {req}</label>
              <input class="input" id="f-email" name="email" type="email" inputmode="email" autocomplete="email" required data-validate aria-describedby="e-email" aria-invalid="false">
              <p class="error" id="e-email"></p>
            </div>

            <div class="field">
              <label for="f-day">{E(FORM_LABELS[4])} {req}</label>
              <input class="input" id="f-day" name="day" type="text" placeholder="{A(FORM_EX_PLACEHOLDERS['day'])}" required data-validate aria-describedby="e-day" aria-invalid="false">
              <p class="error" id="e-day"></p>
            </div>

            <div class="field">
              <label for="f-message">{E(FORM_LABELS[5])} {req}</label>
              <textarea class="input" id="f-message" name="message" rows="5" placeholder="{A(FORM_EX_PLACEHOLDERS['message'])}" required data-validate aria-describedby="e-message" aria-invalid="false"></textarea>
              <p class="error" id="e-message"></p>
            </div>

            <div class="field">
              <label for="f-time">{E(FORM_LABELS[6])} {req}</label>
              <div class="time-row">
                <input class="input" id="f-time" name="time" type="time" required data-validate aria-describedby="h-time e-time" aria-invalid="false">
                <span class="zone" id="h-time">{E(FORM_LABELS[7])}</span>
              </div>
              <p class="error" id="e-time"></p>
            </div>

            <div class="field">
              <label for="f-phone">{E(FORM_LABELS[8])} {req}</label>
              <input class="input" id="f-phone" name="phone" type="tel" inputmode="tel" autocomplete="tel" required data-validate aria-describedby="e-phone" aria-invalid="false">
              <p class="error" id="e-phone"></p>
            </div>

            <div class="field">
              <label for="f-coverage">Insurance or private pay? {req}</label>
              <select class="input select" id="f-coverage" name="coverage" required data-validate aria-describedby="e-coverage" aria-invalid="false">
                <option value="">Select one</option>
                <option>Private pay</option>
                <option>Aetna</option>
                <option>Cigna</option>
                <option>Florida Blue</option>
                <option>United Healthcare</option>
                <option>Other / not sure</option>
              </select>
              <p class="error" id="e-coverage"></p>
            </div>

            <div class="hp" aria-hidden="true"><label>Leave this field empty<input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></div>

            <div class="submit-row">
              <button class="btn btn--solid" type="submit"><span>{E(FORM_LABELS[9])}</span></button>
            </div>
          </form>

          <div class="thanks" id="thanks" role="status">
            <img src="/assets/img/bloom-blue.webp" alt="" width="282" height="166">
            <p>{E(THANKS[0])}</p>
            <p>{E(THANKS[1])}</p>
          </div>
        </div>

      </div>
    </div>
  </section>
</main>
""" + footer()


# ---------------------------------------------------------------------------
# ALTERNATIVE HOME — the "story" version at /alt/
# ---------------------------------------------------------------------------
def _sents(t):
    parts = re.split(r"(?<=[.!?])\s+", t)
    assert " ".join(parts) == t
    return parts


def _split_at(t, *markers):
    out, rest = [], t
    for m in markers:
        i = rest.index(m)
        out.append(rest[:i].strip()); rest = rest[i:]
    out.append(rest.strip())
    assert " ".join(out) == t, (out, t)
    return out


def panel(num, lead, rest, cls=""):
    body = f"<p>{E(rest)}</p>" if rest else ""
    return (f'<article class="panel glass {cls}" data-reveal><span class="panel-num">{num}</span>'
            f'<p class="lead">{E(lead)}</p>{body}</article>')


# ---- About-card visuals on /alt/ — swap images here (files live in assets/img/) ----------------------
# kind: "photo" = framed in an arch with warm grade + grain · "tile" = full-bleed brand tile
#       "shape" = brand shape centred on a colour (bg: sky | blush | butter | saffron)
ABOUT_CARD_VISUALS = [
    dict(kind="photo", file="about-sunset.webp", alt="Paige on a Gulf-coast beach at sunset, arms raised"),
    dict(kind="shape", file="icon-attune.webp", bg="sky", alt=""),
    dict(kind="tile", file="tile-sunburst.webp", alt=""),
    dict(kind="tile", file="tile-ring.webp", alt=""),
    dict(kind="tile", file="tile-flower.webp", alt=""),
    dict(kind="shape", file="bloom-blue.webp", bg="blush", alt=""),
]


def _card_visual(v, n):
    badge = f'<span class="badge" aria-hidden="true">{n}</span>'
    src, alt = f"/assets/img/{v['file']}", A(v["alt"])
    if v["kind"] == "photo":
        img = f'<img class="arch-photo" src="{src}" alt="{alt}" width="1206" height="1278" loading="lazy">'
        return f'<div class="card-visual card-visual--photo">{img}{badge}</div>'
    if v["kind"] == "shape":
        img = f'<img class="shape" src="{src}" alt="{alt}" loading="lazy">'
        return f'<div class="card-visual card-visual--shape bg-{v["bg"]}">{img}{badge}</div>'
    img = f'<img src="{src}" alt="{alt}" width="900" height="900" loading="lazy">'
    return f'<div class="card-visual">{img}{badge}</div>'


def alt_home():
    p = "root"
    base = "/"
    h1 = _sents(T(p, "You don’t need to have everything"))
    h2 = _sents(T(p, "If your own mind"))
    hero_panels = "\n".join("        " + x for x in (
        panel("01", h1[0], " ".join(h1[1:])), panel("02", h2[0], " ".join(h2[1:]))))

    m1 = _split_at(T(p, "Greetings!"), "Based out of")
    m2 = _sents(T(p, "I blend evidence-based tools"))
    meet_panels = "\n".join("          " + x for x in (
        panel("01", m1[0], m1[1]), panel("02", m2[0], " ".join(m2[1:]))))

    a1, a2, a3 = (_sents(T("about", x)) for x in ("I became a therapist", "I believe that understanding", "I consider myself"))
    titles = ["Why I became a therapist", "Finding clarity", "Reclaiming your power",
              "Standing on your story", "A lifelong student", "Unconditional positive regard"]
    texts = [[a1[0]], [a1[1], a1[2]], [a2[0]], [a2[1]], [a3[0], a3[1]], [a3[2]]]
    assert sum(len(t) for t in texts) == len(a1) + len(a2) + len(a3)
    assert len(ABOUT_CARD_VISUALS) == len(titles)
    cards_html = "\n".join(f"""              <li class="card glass">
                {_card_visual(v, f"{i+1:02d}")}
                <div class="card-body"><h4>{E(t)}</h4>{''.join(f'<p>{E(x)}</p>' for x in ps)}</div>
              </li>""" for i, (v, t, ps) in enumerate(zip(ABOUT_CARD_VISUALS, titles, texts)))

    steps = [("awaken", "icon-awaken", "AWAKEN", "Explore the experiences", "Step 1"),
             ("attune", "icon-attune", "ATTUNE", "Develop a deeper", "Step 2"),
             ("align", "icon-align", "ALIGN", "Turn self-awareness", "Step 3")]
    steps_html = "\n".join(f"""        <article class="step glass step--{k}" data-reveal style="--delay:{i*0.14:.2f}s">
          <span class="step-num">{n}</span>
          <img src="/assets/img/{img}.webp" alt="" width="88" height="88" loading="lazy">
          <h3>{E(X(p, h))}</h3>
          <p>{E(T(p, start))}</p>
        </article>""" for i, (k, img, h, start, n) in enumerate(steps))

    therapy_intro = T("therapy", "I believe the therapeutic relationship")
    reiki_p = T("reiki", "This offering is still")
    sup_p = T("supervision", "Qualified supervision services")
    jung = T(p, "“One does not become")
    desc = T(p, "Greetings!").split(" :)")[0].replace("Greetings! ", "", 1)
    extra = ('<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/fraunces-latin.woff2" crossorigin>\n'
             '<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/nunito-latin.woff2" crossorigin>\n'
             '<link rel="stylesheet" href="/assets/css/alt.css">\n')

    return head("Highly Aligned Therapy — story", desc, extra) + f"""<body class="has-announce page-alt">
{INTRO}
<div class="progress" aria-hidden="true"></div>
{header("home", base)}
<main id="main">

  <section class="a-hero glass-bg" aria-label="Welcome">
    <div class="sparkles" data-sparkles="16" aria-hidden="true"></div>
    <div class="wrap a-hero-grid">
      <div class="a-hero-copy">
        <h1 id="hero-title" data-split>{E(T(p, "come as you are"))}</h1>
        <h2 class="leave" data-split>{E(T(p, ". . .Leave as Yourself"))}</h2>
        <div class="rule" aria-hidden="true"></div>
        <div class="cta-row">
          {inquire_btn()}
          <a class="btn" href="#chapter-1">Start reading</a>
        </div>
      </div>
      <div class="a-hero-art" aria-hidden="true">
        <div class="arch"></div><span class="orb orb--a"></span><span class="orb orb--b"></span>
      </div>
    </div>
  </section>

  <section class="section chapter glass-bg" id="chapter-1" aria-labelledby="ch1-title">
    <div class="wrap">
      <div class="chapter-head" data-reveal>
        <span class="kicker">Chapter one</span>
        <h2 id="ch1-title">{E(T(p, "come as you are"))}</h2>
      </div>
      <div class="panels">
{hero_panels}
      </div>
    </div>
  </section>

  <section class="section chapter glass-bg meet" id="about" aria-labelledby="meet-title">
    <div class="wrap">
      <div class="chapter-head" data-reveal>
        <span class="kicker">Chapter two</span>
        <h2 id="meet-title">{E(X(p, "meet Paige"))}</h2>
      </div>
      <div class="alt-meet-grid">
        <div class="portrait" data-reveal><img src="/assets/img/paige-portrait.webp" width="1085" height="1450" alt="Paige Haile, smiling, outdoors" loading="lazy"></div>
        <div>
          <div class="panels panels--stack">
{meet_panels}
          </div>
          <div class="meet-actions" data-reveal>
            <button class="acc-trigger" id="about-trigger" type="button" aria-expanded="false" aria-controls="about-panel"><span>{E(X(p, "Learn More"))}</span> <span class="acc-sub">about me</span><span class="acc-icon" aria-hidden="true"></span></button>
          </div>
        </div>
      </div>

      <div class="acc-panel" id="about-panel" role="region" aria-label="About Paige">
        <div class="acc-inner">
          <div class="about-body stagger">
            <h3 class="carousel-title" style="--k:0">{E(X(p, "Learn More"))} <em>about me</em></h3>
            <h3 class="about-title about-cards-title" style="--k:0">{E(T("about", "ABOUT paige"))}</h3>
            <ul class="cards" id="about-cards" style="--k:1" tabindex="0" aria-label="About Paige, swipe or scroll for more">
{cards_html}
            </ul>
            <div class="carousel-ui" style="--k:2">
              <p class="swipe-hint" aria-hidden="true"><span>Swipe</span> <span>→</span></p>
              <div class="dots" role="group" aria-label="Choose a card"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="section quote chapter" aria-label="Quote">
    <div class="wrap">
      <figure class="paper-card" data-reveal>
        <img class="bloom" src="/assets/img/bloom-blue.webp" alt="" width="282" height="166" loading="lazy">
        <blockquote><p class="type-quote" data-type>{E(jung)}</p></blockquote>
        {STARS}
        <figcaption>{E(T(p, "— Carl Jung"))}</figcaption>
      </figure>
    </div>
  </section>

  <section class="section journey chapter" aria-labelledby="journey-title">
    <div class="wrap">
      <div class="journey-title" data-reveal>
        <span class="kicker">Chapter three</span>
        <h2 id="journey-title">{E(X(p, "The Journey"))}</h2>
        {STARS}
      </div>
      <div class="journey-grid">
{steps_html}
      </div>
    </div>
    <button class="pause-btn" type="button" aria-pressed="false" aria-label="Pause background animation">
      <svg class="i-pause" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 1.5v11M11 1.5v11" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>
      <svg class="i-play" viewBox="0 0 14 14" aria-hidden="true"><path d="M3.5 1.8v10.4L12 7z" fill="currentColor"/></svg>
    </button>
  </section>

  <section class="section teasers chapter glass-bg" aria-labelledby="teasers-title">
    <div class="wrap">
      <div class="teasers-head" data-reveal>
        <div><span class="kicker">Chapter four</span><h2 id="teasers-title">Services</h2></div>
        <a class="link-arrow" href="/services/">See all services {ARROW}</a>
      </div>
      <div class="teaser-grid">
        <article class="teaser teaser--main glass" data-reveal>
          <div><span class="tag">Available now</span></div>
          <h3>{E(X(p, "Therapy", ("header",)))}</h3>
          <p>{E(sentences(therapy_intro, 2))}</p>
          <div class="teaser-links">
            {inquire_btn()}
            <a class="link-arrow" href="/services/#therapy">{E(X(p, "Learn more"))} {ARROW}</a>
          </div>
        </article>
        <article class="teaser teaser--soon glass" data-reveal style="--delay:.1s">
          <h3>{soon_title(T("reiki", "Reiki Services"))}</h3>
          <p>{E(sentences(reiki_p, 2))}</p>
          <div class="teaser-links"><a class="link-arrow" href="/services/#reiki">{E(X(p, "Learn more"))} {ARROW}</a></div>
        </article>
        <article class="teaser teaser--soon glass" data-reveal style="--delay:.2s">
          <h3>{soon_title(T("supervision", "Qualified Supervision"))}</h3>
          <p>{E(sentences(sup_p, 2))}</p>
          <div class="teaser-links"><a class="link-arrow" href="/services/#supervision">{E(X(p, "Learn more"))} {ARROW}</a></div>
        </article>
      </div>
    </div>
  </section>

  <section class="section closing" aria-labelledby="closing-title">
    <div class="sparkles" data-sparkles="10" aria-hidden="true"></div>
    <div class="wrap">
      <h2 id="closing-title" data-reveal>{E(X(p, "Lets Align."))}</h2>
      <div class="cta-row" data-reveal style="--delay:.1s">
        <a class="btn" href="/services/#therapy">{E(X(p, "Learn more"))}</a>
        {inquire_btn()}
      </div>
      <p class="btn-note" style="margin-inline:auto">Share a few details and I’ll be in touch.</p>
    </div>
  </section>

</main>
""" + footer('<li><a href="/classic/">See the original home page</a></li>', base)


def stub(target, label):
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<title>Redirecting…</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<script>location.replace({json.dumps(target)});</script>
</head>
<body><p>This page has moved. <a href="{target}">Continue to {label}</a>.</p></body>
</html>
"""


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", rel, f"({len(content):,} bytes)")


if __name__ == "__main__":
    write("index.html", alt_home())
    write("services/index.html", services())
    write("consultation/index.html", consultation())
    # old Squarespace URLs keep working
    write("classic/index.html", home())
    write("alt/index.html", stub("/", "the home page"))
    write("about/index.html", stub("/#about", "About"))
    write("therapy/index.html", stub("/services/#therapy", "Therapy"))
    write("reiki/index.html", stub("/services/#reiki", "Reiki"))
    write("supervision/index.html", stub("/services/#supervision", "Qualified Supervision"))
    write("home/index.html", stub("/", "the home page"))
