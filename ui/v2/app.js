// Pebble v2 — shared state, API calls, and screen routing.
//
// State lives in sessionStorage under "pebble.brief" (the brief being built)
// and "pebble.plan" (the Plan returned by /api/plan). Each screen reads
// what it needs and writes back what changed. No framework — vanilla JS so
// the page works the moment the HTML loads, no hydration delay.
//
// Flow: welcome → intake (3 Qs) → thinking → plan-review → workspace → publish.

(() => {
  "use strict";

  // ---- State helpers ----
  const STORAGE_KEY_BRIEF = "pebble.brief";
  const STORAGE_KEY_PLAN  = "pebble.plan";
  const STORAGE_KEY_INTAKE_STEP = "pebble.intakeStep";

  function getBrief() {
    try { return JSON.parse(sessionStorage.getItem(STORAGE_KEY_BRIEF) || "{}"); }
    catch { return {}; }
  }
  function setBrief(b) {
    sessionStorage.setItem(STORAGE_KEY_BRIEF, JSON.stringify(b));
  }
  function patchBrief(patch) {
    setBrief({ ...getBrief(), ...patch });
  }
  function getPlan() {
    try { return JSON.parse(sessionStorage.getItem(STORAGE_KEY_PLAN) || "null"); }
    catch { return null; }
  }
  function setPlan(p) {
    sessionStorage.setItem(STORAGE_KEY_PLAN, JSON.stringify(p));
  }

  // ---- API helpers ----
  async function postJSON(path, body) {
    const resp = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const text = await resp.text();
    let json;
    try { json = JSON.parse(text); } catch { json = { error: text || "non-json response" }; }
    if (!resp.ok) throw new Error(json.error || `HTTP ${resp.status}`);
    return json;
  }

  // ---- Navigation ----
  function go(screen) {
    location.href = `/v2/${screen}.html`;
  }

  // ---- AI log writer (organic modernism touch) ----
  function aiLog(message, targetId = "ai-log") {
    const el = document.getElementById(targetId);
    if (!el) return;
    const ts = new Date().toLocaleTimeString();
    const line = document.createElement("p");
    line.innerHTML = `<span class="text-primary">[${ts}]</span> ${message}`;
    el.appendChild(line);
    el.scrollTop = el.scrollHeight;
  }

  // ===========================================================
  // WELCOME (welcome.html) — capture initial idea, derive business_type
  // ===========================================================
  function initWelcome() {
    const textarea = document.getElementById("pebble-idea");
    const startBtn = document.getElementById("pebble-start");
    const log = document.getElementById("ai-log");
    if (!textarea || !startBtn) return;

    // Hydrate from saved state
    const brief = getBrief();
    if (brief.extra_context) textarea.value = brief.extra_context;

    // Starter chip prefill
    document.querySelectorAll(".starter-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        textarea.value = chip.dataset.prompt || chip.textContent.trim();
        textarea.focus();
        if (log) {
          log.innerHTML = '<p class="text-primary">> Got it. Ready when you are.</p>';
        }
      });
    });

    textarea.addEventListener("input", () => {
      if (!log) return;
      if (textarea.value.trim()) {
        log.innerHTML = '<p class="text-primary">> Listening. Press Start when ready.</p>';
      } else {
        log.innerHTML = '<p class="opacity-60">Waiting for your input...</p>';
      }
    });

    startBtn.addEventListener("click", () => {
      const idea = textarea.value.trim();
      if (!idea) {
        textarea.focus();
        textarea.classList.add("ring-2", "ring-error");
        setTimeout(() => textarea.classList.remove("ring-2", "ring-error"), 600);
        return;
      }
      patchBrief({
        extra_context: idea,
        business_name: brief.business_name || "Untitled Project",
      });
      sessionStorage.removeItem(STORAGE_KEY_INTAKE_STEP);
      go("intake");
    });
  }

  // ===========================================================
  // INTAKE (intake.html) — 3 Qs: audience, primary action, style
  // ===========================================================
  const INTAKE_STEPS = [
    {
      key: "audience",
      multi: true,
      headline: "Who walks in your door?",
      subhead: "Don't overthink it — locals, tourists, professionals, whoever you serve.",
      chips: [
        { id: "locals",       label: "Locals",        icon: "home_pin" },
        { id: "travelers",    label: "Travelers",     icon: "travel_explore" },
        { id: "professionals",label: "Professionals", icon: "work" },
        { id: "families",     label: "Families",      icon: "family_restroom" },
        { id: "enthusiasts",  label: "Enthusiasts",   icon: "star" },
        { id: "other",        label: "Other",         icon: "more_horiz" },
      ],
    },
    {
      key: "site_functions",
      multi: true,
      headline: "What's the main thing visitors should do?",
      subhead: "Pick what matters. Pebble adds the right page for each.",
      chips: [
        { id: "presence",  label: "See your story",       icon: "auto_stories" },
        { id: "leads",     label: "Get in touch",         icon: "mail" },
        { id: "booking",   label: "Book an appointment",  icon: "event" },
        { id: "ecommerce", label: "Buy something",        icon: "shopping_bag" },
        { id: "portfolio", label: "See your work",        icon: "collections" },
        { id: "payment",   label: "Pay or donate",        icon: "payments" },
      ],
    },
    {
      key: "brand_tone",
      multi: false,
      headline: "What feeling should it give off?",
      subhead: "One word that captures the mood.",
      chips: [
        { id: "warm",         label: "Warm",         icon: "wb_sunny" },
        { id: "professional", label: "Professional", icon: "workspace_premium" },
        { id: "bold",         label: "Bold",         icon: "bolt" },
        { id: "calm",         label: "Calm",         icon: "spa" },
        { id: "playful",      label: "Playful",      icon: "celebration" },
        { id: "premium",      label: "Premium",      icon: "diamond" },
      ],
    },
  ];

  function initIntake() {
    const chipsEl = document.getElementById("intake-chips");
    const headline = document.getElementById("intake-question");
    const subhead = document.getElementById("intake-subhead");
    const continueBtn = document.getElementById("intake-continue");
    const backBtn = document.getElementById("intake-back");
    const skipBtn = document.getElementById("intake-skip");
    const progress = document.getElementById("intake-progress");
    if (!chipsEl || !headline || !continueBtn) return;

    let stepIdx = parseInt(sessionStorage.getItem(STORAGE_KEY_INTAKE_STEP) || "0", 10);
    if (isNaN(stepIdx) || stepIdx < 0) stepIdx = 0;
    if (stepIdx >= INTAKE_STEPS.length) stepIdx = INTAKE_STEPS.length - 1;

    const selections = { __multi: {} }; // per-step state

    function renderStep() {
      const step = INTAKE_STEPS[stepIdx];
      headline.textContent = step.headline;
      subhead.textContent = step.subhead;

      // Progress dots
      if (progress) {
        progress.querySelectorAll("[data-step]").forEach((dot, i) => {
          if (i === stepIdx) {
            dot.className = "w-2 h-2 rounded-full bg-primary ring-4 ring-primary-fixed/30";
          } else if (i < stepIdx) {
            dot.className = "w-2 h-2 rounded-full bg-secondary";
          } else {
            dot.className = "w-2 h-2 rounded-full bg-outline-variant";
          }
        });
      }

      // Render chips
      const brief = getBrief();
      const existing = brief[step.key];
      const selectedSet = new Set();
      if (Array.isArray(existing)) existing.forEach((x) => selectedSet.add(x));
      else if (typeof existing === "string" && existing) selectedSet.add(existing);

      chipsEl.innerHTML = "";
      step.chips.forEach((chip) => {
        const btn = document.createElement("button");
        btn.dataset.chipId = chip.id;
        const isSelected = selectedSet.has(chip.id);
        btn.className = "group relative flex flex-col items-center justify-center gap-sm p-lg rounded-xl transition-all active:scale-95 " +
          (isSelected
            ? "bg-secondary-container border border-secondary text-on-secondary-container"
            : "bg-surface-container border border-outline-variant hover:bg-surface-bright");
        btn.innerHTML = `
          <span class="material-symbols-outlined ${isSelected ? '' : 'text-on-surface-variant group-hover:text-primary'}">${chip.icon}</span>
          <span class="font-label-md text-label-md">${chip.label}</span>
          ${isSelected ? '<div class="absolute top-2 right-2"><span class="material-symbols-outlined text-on-secondary-container text-sm" style="font-variation-settings: \'FILL\' 1;">check_circle</span></div>' : ''}
        `;
        btn.addEventListener("click", () => {
          if (step.multi) {
            if (selectedSet.has(chip.id)) selectedSet.delete(chip.id);
            else selectedSet.add(chip.id);
            patchBrief({ [step.key]: Array.from(selectedSet) });
          } else {
            selectedSet.clear();
            selectedSet.add(chip.id);
            patchBrief({ [step.key]: chip.id });
          }
          renderStep();
        });
        chipsEl.appendChild(btn);
      });

      aiLog(`> Question ${stepIdx + 1} of ${INTAKE_STEPS.length}: ${step.key}`);
    }

    continueBtn.addEventListener("click", () => {
      if (stepIdx < INTAKE_STEPS.length - 1) {
        stepIdx += 1;
        sessionStorage.setItem(STORAGE_KEY_INTAKE_STEP, String(stepIdx));
        renderStep();
      } else {
        // After Q3: derive business_type from extra_context + chips and fetch Plan
        const brief = getBrief();
        const idea = (brief.extra_context || "").toLowerCase();
        // Cheap heuristic — engine's industry resolver will refine via fuzzy match + LLM fallback.
        let bt = brief.business_type;
        if (!bt) {
          const hints = [
            ["bakery","bakery"],["restaurant","restaurant"],["coffee","cafe"],["cafe","cafe"],
            ["dentist","dentist"],["yoga","yoga_studio"],["plumb","plumbing"],["hvac","hvac"],
            ["lawyer","law_firm"],["attorney","law_firm"],["real estate","real_estate"],
            ["photo","photography"],["therapist","therapist"],["salon","hair_salon"],
            ["barber","barbershop"],["spa","spa"],["fitness","gym"],["gym","gym"],
            ["pet","pet_grooming"],["clean","cleaning_service"],["landscap","landscaping"],
            ["construct","construction"],["consult","consultant"],["agency","agency"],
            ["jewel","jeweler"],["car","auto_repair"],["auto","auto_repair"],
          ];
          for (const [needle, key] of hints) {
            if (idea.includes(needle)) { bt = key; break; }
          }
          bt = bt || "small_business";
          patchBrief({ business_type: bt });
        }
        sessionStorage.removeItem(STORAGE_KEY_INTAKE_STEP);
        go("thinking");
      }
    });

    if (backBtn) {
      backBtn.addEventListener("click", () => {
        if (stepIdx > 0) {
          stepIdx -= 1;
          sessionStorage.setItem(STORAGE_KEY_INTAKE_STEP, String(stepIdx));
          renderStep();
        } else {
          go("welcome");
        }
      });
    }
    if (skipBtn) {
      skipBtn.addEventListener("click", () => {
        sessionStorage.removeItem(STORAGE_KEY_INTAKE_STEP);
        go("thinking");
      });
    }

    renderStep();
  }

  // ===========================================================
  // THINKING (thinking.html) — fetch plan, then advance to plan-review
  // ===========================================================
  const THINKING_STEPS = [
    { id: "industry", icon: "search",     label: "Reading your industry",   detail: "I'm looking up what websites for your type of business usually include." },
    { id: "style",    icon: "palette",    label: "Choosing a style",        detail: "I'm picking a visual style that matches the feeling you chose." },
    { id: "pages",    icon: "edit_note",  label: "Writing the pages",       detail: "I'm drafting the pages your industry typically needs." },
    { id: "photos",   icon: "image",      label: "Finding photos",          detail: "I'm pulling stock photos that match your industry." },
    { id: "checks",   icon: "rule",       label: "Checking my work",        detail: "I'm running 32 quality checks before you see the draft." },
    { id: "ready",    icon: "check_circle", label: "Ready to show you",     detail: "All set. Let's review." },
  ];

  function renderTimeline(activeIdx) {
    const tl = document.getElementById("timeline");
    if (!tl) return;
    // Keep the absolute connector line as the first child
    const connector = tl.querySelector(".absolute");
    tl.innerHTML = "";
    if (connector) tl.appendChild(connector);
    THINKING_STEPS.forEach((step, i) => {
      const wrap = document.createElement("div");
      const state = i < activeIdx ? "done" : (i === activeIdx ? "active" : "pending");
      wrap.className = "flex gap-md relative z-10" + (state === "pending" ? " opacity-60" : "");
      const dotClasses = state === "done"
        ? "bg-secondary-container border-outline-variant"
        : state === "active"
          ? "bg-primary-container border-primary shadow-sm"
          : "bg-surface-container border-outline-variant";
      const icon = state === "done" ? "check_circle" : step.icon;
      const iconFill = state === "done" ? `style="font-variation-settings: 'FILL' 1;"` : "";
      wrap.innerHTML = `
        <div class="w-10 h-10 rounded-full ${dotClasses} flex items-center justify-center border">
          <span class="material-symbols-outlined ${state === 'active' ? 'text-on-primary-container' : (state === 'done' ? 'text-on-secondary-container' : 'text-outline')}" ${iconFill}>${icon}</span>
        </div>
        <div>
          <p class="font-label-md text-label-md ${state === 'active' ? 'text-primary flex items-center gap-sm' : 'text-on-surface'}">
            ${step.label}
            ${state === "active" ? '<span class="w-2 h-2 rounded-full bg-primary animate-pulse"></span>' : ""}
          </p>
          <p class="text-on-surface-variant text-sm mt-xs">${step.detail}</p>
        </div>
      `;
      tl.appendChild(wrap);
    });
  }

  async function initThinking() {
    const tl = document.getElementById("timeline");
    if (!tl) return;
    renderTimeline(0);
    aiLog(`> Starting build for "${getBrief().business_name || 'your project'}"...`, "ai-log-detail");

    // Sequence the visible timeline with the real /api/plan call.
    // We can't subscribe to engine progress, so we advance on a soft cadence
    // while the request is in flight and snap to the final state on response.
    const brief = getBrief();
    let advance = 0;
    const interval = setInterval(() => {
      advance = Math.min(advance + 1, THINKING_STEPS.length - 1);
      renderTimeline(advance);
      aiLog(`> ${THINKING_STEPS[advance].label}...`, "ai-log-detail");
    }, 1200);

    try {
      const result = await postJSON("/api/plan", brief);
      clearInterval(interval);
      renderTimeline(THINKING_STEPS.length - 1);
      setPlan(result.plan);
      patchBrief({
        _industry_intel_key: result.industry_key,
        _design_dna_id: result.dna_id,
      });
      aiLog(`> Plan ready — ${result.plan.pages.length} pages, ${result.plan.features.length} features.`, "ai-log-detail");
      setTimeout(() => go("plan-review"), 600);
    } catch (e) {
      clearInterval(interval);
      aiLog(`> Error: ${e.message}`, "ai-log-detail");
      alert(`Plan generation failed: ${e.message}`);
    }
  }

  // ===========================================================
  // PLAN REVIEW (plan-review.html) — render the Plan, generate on confirm
  // ===========================================================
  function initPlanReview() {
    const audience = document.getElementById("plan-audience");
    if (!audience) return;
    const plan = getPlan();
    if (!plan) { go("welcome"); return; }

    audience.textContent = plan.audience;
    document.getElementById("plan-goal").textContent = plan.goal;

    // Pages
    const pagesEl = document.getElementById("plan-pages");
    pagesEl.innerHTML = "";
    plan.pages.forEach((p) => {
      const row = document.createElement("div");
      row.className = "flex items-center justify-between py-sm border-b border-[#D8D1C5] last:border-0";
      row.innerHTML = `
        <div>
          <div class="flex items-center gap-sm">
            <span class="font-bold text-on-surface">${p.title}</span>
            <span class="${p.foundation ? 'bg-secondary-container text-on-secondary-container' : 'bg-tertiary-container text-on-tertiary-container'} text-[10px] px-sm py-xs rounded-full uppercase font-bold">${p.foundation ? 'Foundation' : 'Industry'}</span>
          </div>
          <p class="text-label-md text-on-surface-variant opacity-70">${p.purpose}</p>
        </div>
      `;
      pagesEl.appendChild(row);
    });

    // Features
    const featuresEl = document.getElementById("plan-features");
    featuresEl.innerHTML = "";
    plan.features.forEach((f) => {
      const chip = document.createElement("span");
      chip.className = "bg-surface-container-highest px-md py-sm rounded-full text-label-md";
      chip.textContent = f.label;
      featuresEl.appendChild(chip);
    });

    // Style
    const styleLabel = document.getElementById("plan-style-label");
    const styleMood = document.getElementById("plan-style-mood");
    const stylePalette = document.getElementById("plan-style-palette");
    const styleFonts = document.getElementById("plan-style-fonts");
    if (styleLabel) styleLabel.textContent = `Inspired by ${plan.style.label}`;
    if (styleMood) styleMood.textContent = plan.style.mood || plan.style.label;
    if (stylePalette) {
      stylePalette.innerHTML = "";
      Object.entries(plan.style.palette || {}).forEach(([name, hex]) => {
        if (!hex) return;
        const swatch = document.createElement("div");
        swatch.className = "w-12 h-12 rounded-full border border-outline shadow-sm";
        swatch.style.backgroundColor = hex;
        swatch.title = `${name}: ${hex}`;
        stylePalette.appendChild(swatch);
      });
    }
    if (styleFonts) {
      styleFonts.innerHTML = `
        <p class="font-display-md text-headline-lg text-primary">${plan.style.fonts.display || '—'}</p>
        <p class="font-body-md text-body-md text-on-surface">${plan.style.fonts.body || '—'}</p>
      `;
    }

    // Setup needs
    const setupEl = document.getElementById("plan-setup");
    setupEl.innerHTML = "";
    plan.setup_needs.forEach((s) => {
      const badgeClass = s.status === "auto"
        ? "bg-secondary-container text-on-secondary-container"
        : s.status === "pending"
          ? "bg-tertiary-container text-on-tertiary-container"
          : "bg-surface-variant text-on-surface-variant";
      const badgeLabel = s.status === "auto" ? "Auto" : s.status === "pending" ? "Coming soon" : "You'll do this";
      const row = document.createElement("div");
      row.className = "flex items-center justify-between p-sm bg-surface rounded-lg border border-[#D8D1C5]";
      row.innerHTML = `
        <span class="font-label-md text-on-surface">${s.label}</span>
        <span class="text-[10px] px-2 py-0.5 rounded-full ${badgeClass} font-bold uppercase tracking-wider">${badgeLabel}</span>
      `;
      row.title = s.notes;
      setupEl.appendChild(row);
    });

    // Generate
    document.getElementById("plan-generate").addEventListener("click", async () => {
      const btn = document.getElementById("plan-generate");
      btn.disabled = true;
      btn.textContent = "Generating…";
      try {
        const brief = getBrief();
        const result = await postJSON("/api/generate", brief);
        sessionStorage.setItem("pebble.lastBuild", JSON.stringify(result));
        go("workspace");
      } catch (e) {
        alert(`Generate failed: ${e.message}`);
        btn.disabled = false;
        btn.textContent = "Generate my draft";
      }
    });
  }

  // ===========================================================
  // WORKSPACE (workspace.html) — show generated site in iframe
  // ===========================================================
  function initWorkspace() {
    const iframe = document.getElementById("site-preview");
    if (!iframe) return;
    const last = JSON.parse(sessionStorage.getItem("pebble.lastBuild") || "null");
    if (!last) { go("welcome"); return; }
    const previewUrl = last.preview_url || `/preview/${last.slug}/`;
    iframe.src = previewUrl;
    const urlEl = document.getElementById("preview-url");
    if (urlEl) urlEl.textContent = `${last.slug}.pebble.site`;
    const nameEl = document.getElementById("workspace-project-name");
    if (nameEl) nameEl.textContent = getBrief().business_name || "Untitled Project";

    // Launch Setup list (from plan.setup_needs)
    const plan = getPlan();
    const setupListEl = document.getElementById("launch-setup-list");
    if (plan && setupListEl) {
      setupListEl.innerHTML = "";
      plan.setup_needs.forEach((s) => {
        const badgeClass = s.status === "auto"
          ? "bg-secondary-container text-on-secondary-container"
          : s.status === "pending"
            ? "bg-tertiary-container text-on-tertiary-container"
            : "bg-surface-variant text-on-surface-variant";
        const badgeLabel = s.status === "auto" ? "Auto-done" : s.status === "pending" ? "Coming soon" : "You'll do this";
        const row = document.createElement("div");
        row.className = "p-md rounded-xl bg-surface border border-outline-variant flex flex-col gap-sm";
        row.innerHTML = `
          <div class="flex justify-between items-start">
            <span class="font-label-md text-label-md">${s.label}</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full ${badgeClass} font-bold uppercase tracking-wider">${badgeLabel}</span>
          </div>
          <p class="text-xs text-on-surface-variant">${s.notes}</p>
        `;
        setupListEl.appendChild(row);
      });
      const remaining = plan.setup_needs.filter((s) => s.status !== "auto").length;
      const remainEl = document.getElementById("setup-remaining");
      if (remainEl) remainEl.textContent = `${remaining} items remaining`;
    }

    // Refinement chips — stubbed; engine endpoint not yet wired.
    document.querySelectorAll(".refine-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        alert(`"${chip.dataset.refine}" refinement is coming soon — Pebble can't apply this yet.`);
      });
    });

    // Go Live
    document.getElementById("go-live").addEventListener("click", () => {
      go("publish");
    });
  }

  // ===========================================================
  // PUBLISH (publish.html) — show URL + actions
  // ===========================================================
  function initPublish() {
    const urlEl = document.getElementById("published-url");
    if (!urlEl) return;
    const last = JSON.parse(sessionStorage.getItem("pebble.lastBuild") || "null");
    if (last && last.slug) urlEl.textContent = `${last.slug}.pebble.site`;

    const viewBtn = document.getElementById("publish-view");
    if (viewBtn && last) {
      viewBtn.addEventListener("click", () => {
        window.open(last.preview_url || `/preview/${last.slug}/`, "_blank");
      });
    }
    const editBtn = document.getElementById("publish-edit");
    if (editBtn) editBtn.addEventListener("click", () => go("workspace"));
    const shareBtn = document.getElementById("publish-share");
    if (shareBtn) shareBtn.addEventListener("click", () => {
      const text = urlEl.textContent;
      navigator.clipboard?.writeText(text);
      shareBtn.querySelector("span:last-child").textContent = "Copied!";
      setTimeout(() => { shareBtn.querySelector("span:last-child").textContent = "Share"; }, 1500);
    });
  }

  // ---- Page dispatcher ----
  document.addEventListener("DOMContentLoaded", () => {
    const path = location.pathname.replace(/\/$/, "").split("/").pop() || "welcome";
    const name = path.replace(/\.html$/, "");
    const dispatch = {
      "welcome":          initWelcome,
      "":                 initWelcome,
      "v2":               initWelcome,
      "intake":           initIntake,
      "thinking":         initThinking,
      "plan-review":      initPlanReview,
      "workspace":        initWorkspace,
      "workspace-setup":  initWorkspace,
      "explain-mode":     () => {}, // pure visual demo
      "publish":          initPublish,
    };
    (dispatch[name] || initWelcome)();
  });
})();
