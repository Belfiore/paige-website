/* Highly Aligned Therapy — interactions
   Intro reveal · nav · About accordion · scroll reveals · sparkles · form */
(() => {
  "use strict";

  const doc = document.documentElement;
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const base = (($(".brand") || {}).getAttribute && $(".brand").getAttribute("href")) || "/";
  const isHome = location.pathname === base || location.pathname === base + "index.html";

  /* ------------------------------------------------------------------
     Sparkles — small gold stars, seeded so the layout is stable
  ------------------------------------------------------------------ */
  function seeded(seed) {
    let s = seed >>> 0;
    return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  }
  $$("[data-sparkles]").forEach((box, bi) => {
    const n = parseInt(box.dataset.sparkles, 10) || 10;
    const rnd = seeded(7919 * (bi + 3));
    for (let i = 0; i < n; i++) {
      const el = document.createElement("span");
      el.className = "sparkle";
      el.style.setProperty("--x", (rnd() * 96 + 1).toFixed(1) + "%");
      el.style.setProperty("--y", (rnd() * 94 + 2).toFixed(1) + "%");
      el.style.setProperty("--s", (8 + rnd() * 12).toFixed(0) + "px");
      el.style.setProperty("--d", (3 + rnd() * 3.5).toFixed(2) + "s");
      el.style.setProperty("--delay", (-rnd() * 6).toFixed(2) + "s");
      box.appendChild(el);
    }
  });

  /* ------------------------------------------------------------------
     Word-by-word headline reveal
  ------------------------------------------------------------------ */
  $$("[data-split]").forEach((el) => {
    const tokens = el.textContent.trim().split(/\s+/);
    // keep "..." tokens glued to their neighbour so the dots never wrap alone
    const dots = (t) => /^\.+$/.test(t);
    const groups = [];
    tokens.forEach((t) => {
      const last = groups[groups.length - 1];
      if (last && (dots(t) || last.every(dots))) last.push(t); else groups.push([t]);
    });
    el.textContent = "";
    let i = 0;
    groups.forEach((g, gi) => {
      const nw = document.createElement("span");
      nw.className = "nw";
      g.forEach((word, wi) => {
        const outer = document.createElement("span");
        outer.className = "w";
        const inner = document.createElement("span");
        inner.style.setProperty("--i", i++);
        inner.textContent = word;
        outer.appendChild(inner);
        nw.appendChild(outer);
        if (wi < g.length - 1) nw.appendChild(document.createTextNode(" "));
      });
      el.appendChild(nw);
      if (gi < groups.length - 1) el.appendChild(document.createTextNode(" "));
    });
    el.classList.add("js-split-ready");
  });

  /* ------------------------------------------------------------------
     Intro — a bloom, then an iris that opens onto the page
  ------------------------------------------------------------------ */
  let resolveIntro;
  const introDone = new Promise((r) => (resolveIntro = r));
  const intro = $("#intro");

  function endIntro() {
    if (intro) intro.classList.add("is-gone");
    doc.classList.remove("intro-pending");
    doc.classList.add("intro-done");
    resolveIntro();
  }

  if (intro && doc.classList.contains("intro-pending")) {
    try { sessionStorage.setItem("hat-intro", "1"); } catch (e) { /* private mode */ }

    // orbiting sparkles around the logo
    const orbit = $(".intro-orbit", intro);
    const count = 9;
    for (let i = 0; i < count; i++) {
      const s = document.createElement("i");
      s.style.setProperty("--a", (i * 360) / count + (i % 2 ? 14 : -6) + "deg");
      s.style.setProperty("--rad", (i % 3 === 0 ? 46 : 41) + "%");
      s.style.setProperty("--n", i);
      s.style.setProperty("--sc", i % 2 ? 0.7 : 1.15);
      orbit.appendChild(s);
    }

    let skipped = false;
    const timers = [];
    const later = (fn, ms) => timers.push(setTimeout(fn, ms));
    const supportsIris = !!(window.CSS && CSS.registerProperty);

    const open = () => {
      if (skipped) return;
      if (supportsIris) {
        intro.classList.add("is-opening");
        // only the iris on the overlay itself may end the intro (child animations bubble up)
        intro.addEventListener("animationend", (e) => { if (e.target === intro && e.animationName === "iris") endIntro(); });
        later(endIntro, 1700); // safety net
      } else {
        intro.classList.add("is-fading");
        later(endIntro, 520);
      }
    };

    const skip = () => {
      if (skipped) return;
      skipped = true;
      timers.forEach(clearTimeout);
      intro.classList.add("is-fading");
      setTimeout(endIntro, 320);
    };
    ["pointerdown", "keydown"].forEach((ev) => addEventListener(ev, skip, { once: true, passive: true }));

    // start the clock once the logo is ready (never wait more than ~1s)
    const logo = $(".intro-logo", intro);
    const ready = logo && logo.decode ? Promise.race([logo.decode().catch(() => {}), new Promise((r) => setTimeout(r, 1000))]) : Promise.resolve();
    ready.then(() => later(open, 1500));
    later(endIntro, 6000); // hard stop: never trap the page
  } else {
    doc.classList.add("intro-done");
    resolveIntro();
  }

  /* ------------------------------------------------------------------
     Scroll reveals
  ------------------------------------------------------------------ */
  const revealables = $$("[data-reveal], [data-split]");
  if ("IntersectionObserver" in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        introDone.then(() => e.target.classList.add("is-in"));
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    revealables.forEach((el) => io.observe(el));
  } else {
    revealables.forEach((el) => el.classList.add("is-in"));
  }

  /* ------------------------------------------------------------------
     Light parallax on the hero photograph
  ------------------------------------------------------------------ */
  const heroWrap = $(".hero-wrap");
  const heroMedia = heroWrap && $(".hero-media", heroWrap);
  if (heroMedia && !reduceMotion) {
    let ticking = false;
    const update = () => {
      ticking = false;
      const r = heroWrap.getBoundingClientRect();
      if (r.bottom < 0 || r.top > innerHeight) return;
      const y = Math.max(-54, Math.min(54, r.top * 0.14));
      heroMedia.style.setProperty("--py", y.toFixed(1) + "px");
    };
    addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }

  /* ------------------------------------------------------------------
     Navigation — mobile menu + Services dropdown
  ------------------------------------------------------------------ */
  const nav = $("#primary-nav");
  const menuBtn = $(".menu-toggle");
  const setMenu = (open) => {
    if (!nav || !menuBtn) return;
    nav.classList.toggle("open", open);
    menuBtn.setAttribute("aria-expanded", String(open));
    $(".menu-label", menuBtn).textContent = open ? "Close Menu" : "Open Menu";
  };
  if (menuBtn) menuBtn.addEventListener("click", () => setMenu(!nav.classList.contains("open")));

  const sub = $(".has-sub");
  const subBtn = sub && $(".sub-toggle", sub);
  let subTimer;
  const setSub = (open) => {
    if (!sub) return;
    sub.classList.toggle("open", open);
    subBtn.setAttribute("aria-expanded", String(open));
  };
  if (sub) {
    subBtn.addEventListener("click", () => setSub(!sub.classList.contains("open")));
    sub.addEventListener("mouseenter", () => { clearTimeout(subTimer); if (matchMedia("(hover:hover)").matches) setSub(true); });
    sub.addEventListener("mouseleave", () => { subTimer = setTimeout(() => setSub(false), 180); });
    sub.addEventListener("focusin", () => setSub(true));
    sub.addEventListener("focusout", (e) => { if (!sub.contains(e.relatedTarget)) setSub(false); });
  }
  addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (sub && sub.classList.contains("open")) { setSub(false); subBtn.focus(); }
    if (nav && nav.classList.contains("open")) { setMenu(false); menuBtn.focus(); }
  });
  document.addEventListener("click", (e) => {
    if (nav && nav.classList.contains("open") && !e.target.closest(".header-inner")) setMenu(false);
    if (sub && !sub.contains(e.target)) setSub(false);
  });
  $$("#primary-nav a").forEach((a) => a.addEventListener("click", () => { setMenu(false); setSub(false); }));

  /* ------------------------------------------------------------------
     About accordion (merged About page) — deep link: /#about
  ------------------------------------------------------------------ */
  const trigger = $("#about-trigger");
  const panel = $("#about-panel");
  const aboutSection = $("#about");

  function setAbout(open, { scroll = false } = {}) {
    if (!trigger || !panel) return;
    trigger.setAttribute("aria-expanded", String(open));
    panel.classList.toggle("open", open);
    if (open) panel.removeAttribute("inert"); else panel.setAttribute("inert", "");
    if (open && scroll) {
      setTimeout(() => {
        const top = panel.getBoundingClientRect().top;
        if (top > innerHeight * 0.55) $(".about-body", panel).scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
      }, 260);
    }
  }
  if (trigger && panel) {
    panel.setAttribute("inert", "");
    trigger.addEventListener("click", () => setAbout(trigger.getAttribute("aria-expanded") !== "true", { scroll: true }));
    const syncHash = () => {
      if (location.hash === "#about") {
        setAbout(true);
        requestAnimationFrame(() => aboutSection.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" }));
      }
    };
    addEventListener("hashchange", syncHash);
    if (location.hash === "#about") introDone.then(syncHash);
    $$("[data-open-about]").forEach((a) => a.addEventListener("click", (e) => {
      if (!isHome) return; // other pages navigate to /#about normally
      e.preventDefault();
      history.replaceState(null, "", base + "#about");
      syncHash();
    }));
  }

  /* ------------------------------------------------------------------
     Journey background — pause control
  ------------------------------------------------------------------ */
  const pauseBtn = $(".pause-btn");
  if (pauseBtn) {
    const journey = pauseBtn.closest(".journey");
    pauseBtn.addEventListener("click", () => {
      const paused = journey.toggleAttribute("data-paused");
      pauseBtn.setAttribute("aria-pressed", String(paused));
      pauseBtn.setAttribute("aria-label", paused ? "Play background animation" : "Pause background animation");
    });
  }

  /* ------------------------------------------------------------------
     Consultation inquiry form
  ------------------------------------------------------------------ */
  const form = $("#inquiry");
  if (form) {
    const getEndpoint = () => (($('meta[name="inquiry-endpoint"]') || {}).content || "").trim();
    const alertBox = $(".form-alert"); // sits above the form, so search the document
    // single source of truth for the booking URL: the page's own Grow button
    const growHref = (($("[data-grow]") || {}).href || "").replace(/&/g, "&amp;");
    const growLink = growHref ? `<a href="${growHref}" target="_blank" rel="noopener noreferrer">Grow Therapy</a>` : "Grow Therapy";
    const submitBtn = $('button[type="submit"]', form);
    const thanks = $("#thanks");

    const rules = {
      first: (v) => (v.trim() ? "" : "Please enter your first name."),
      last: (v) => (v.trim() ? "" : "Please enter your last name."),
      email: (v) => !v.trim() ? "Please enter your email address." : /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v.trim()) ? "" : "Please enter a valid email address, like name@example.com.",
      day: (v) => (v.trim() ? "" : "Please enter a preferred day."),
      message: (v) => (v.trim() ? "" : "Please add a short message."),
      time: (v) => (v ? "" : "Please choose a preferred time."),
      phone: (v) => !v.trim() ? "Please enter your phone number." : v.replace(/\D/g, "").length >= 10 ? "" : "Please enter a phone number with at least 10 digits.",
    };

    const fieldOf = (input) => input.closest(".field");
    function check(input) {
      const rule = rules[input.name];
      if (!rule) return true;
      const msg = rule(input.value);
      const field = fieldOf(input);
      const err = $(".error", field);
      field.classList.toggle("has-error", !!msg);
      input.setAttribute("aria-invalid", msg ? "true" : "false");
      if (err) err.textContent = msg;
      return !msg;
    }
    const inputs = $$("[data-validate]", form);
    inputs.forEach((i) => {
      i.addEventListener("blur", () => { if (i.value || i.getAttribute("aria-invalid") === "true") check(i); });
      i.addEventListener("input", () => { if (i.getAttribute("aria-invalid") === "true") check(i); });
    });

    const fmtTime = (hhmm) => {
      const [h, m] = hhmm.split(":").map(Number);
      return `${((h + 11) % 12) + 1}:${String(m).padStart(2, "0")} ${h < 12 ? "AM" : "PM"} Eastern Time`;
    };
    const showAlert = (html) => { alertBox.innerHTML = html; alertBox.classList.add("show"); alertBox.focus(); };

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      alertBox.classList.remove("show");
      const bad = inputs.filter((i) => !check(i));
      if (bad.length) {
        showAlert("Please fix the highlighted fields and try again.");
        bad[0].focus();
        return;
      }
      const data = new FormData(form);
      if (data.get("_gotcha")) return; // honeypot
      data.set("preferred_time_readable", fmtTime(data.get("time")));
      data.set("_subject", "Consultation Inquiry");

      const endpoint = getEndpoint();
      if (!endpoint) {
        console.warn("[inquiry] No endpoint configured. Set <meta name=\"inquiry-endpoint\"> in consultation/index.html.");
        showAlert(`This form isn’t connected to email yet, so your message was not sent. You can book directly through ${growLink} in the meantime.`);
        return;
      }
      submitBtn.disabled = true;
      const label = submitBtn.firstElementChild;
      const original = label.textContent;
      label.textContent = "Sending…";
      try {
        const res = await fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } });
        if (!res.ok) throw new Error("HTTP " + res.status);
        form.hidden = true;
        alertBox.classList.remove("show");
        const formIntro = $(".form-intro");
        if (formIntro) formIntro.hidden = true;
        thanks.classList.add("show");
        thanks.setAttribute("tabindex", "-1");
        thanks.focus();
        thanks.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "center" });
      } catch (err) {
        showAlert(`Something went wrong and your message was not sent. Please try again, or book directly through ${growLink}.`);
        submitBtn.disabled = false;
        label.textContent = original;
      }
    });
  }
})();
