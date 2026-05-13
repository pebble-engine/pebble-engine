# Pebble Engine

A local website briefing engine for sites that don't look generated.

The brain of Pebble. Answer fourteen questions in a visual, quiz-style interface; the engine pipes them through a BM25 design-system search, runs an anti-slop audit, and either (a) hands you a master prompt to paste into Antigravity, or (b) calls Claude directly and writes a working website to disk for you.

---

## Run it

```bash
cd pebble-engine
python3 pebble_engine.py
```

Browser opens at `http://localhost:8000`. The basic flow needs zero `pip install` and zero config.

If port 8000 is taken: `python3 pebble_engine.py --port 8765`.

---

## Two operating modes

### Mode A — Prompt only (default, no config needed)

Take the quiz, copy or download the generated `PROMPT.md`, paste into Antigravity's agent panel. Gemini reads your `skills/` folder and builds the site. This is the original flow and works out of the box.

### Mode B — Auto-build (Pebble Engine calls Claude for you)

The engine itself calls the Anthropic API with the full brief, parses the response into files, and writes them to `output/<slug>/site/`. You see a preview link the moment it's done — no copy-pasting, no context-switching to a chat panel.

To enable Mode B:

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and paste your ANTHROPIC_API_KEY
```

Get a key at [console.anthropic.com](https://console.anthropic.com/settings/keys).

When the server starts, the banner tells you which mode is available:

```
   Pebble Engine
   ui-ux-pro-max engine: loaded
   auto-build mode:      ready
   model:                claude-sonnet-4-6
```

If auto-build isn't ready, the quiz still runs in Mode A. The choice between the two appears as a fork after the quiz, and the "build now" card greys out when auto-build is unavailable.

---

## The Antigravity workflow

Pebble Engine is built around this loop:

1. Open the `pebble-engine/` folder as a workspace in Antigravity. The `skills/` directory becomes available to Gemini automatically.
2. Open Antigravity's terminal and run `python3 pebble_engine.py`. The quiz opens in your browser.
3. Answer the quiz questions. `Enter` advances, `Esc` goes back, `Cmd/Ctrl+Enter` advances inside a textarea.
4. Pick your path:
   - **Mode A:** Click "Just give me the prompt" → copy or download → paste into Antigravity's agent.
   - **Mode B:** Click "Build the site now" → wait ~30–90 seconds → click "Preview the site."
5. Once the site exists in `output/<slug>/site/`, use the other skills the way they're meant to be used:
   - `code-reviewer` for a security/quality pass on the generated files
   - `readme-generator` for the project's README
   - `git-commit-writer` for clean commits as you iterate

Either way, you stay visual. The only "terminal moment" is the one command to start the engine.

---

## Folder structure

```
pebble-engine/
├── pebble_engine.py             ← run this
├── README.md                    ← you are here
├── requirements.txt             ← optional: pip install for auto-build
├── .env.example                 ← copy to .env, add your API key
├── ui/
│   └── index.html               ← the quiz (single file, self-contained)
├── skills/
│   ├── no-slop-web/             ← anti-slop doctrine
│   ├── ui-ux-pro-max/           ← BM25 design system search
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── core.py
│   │   │   ├── search.py
│   │   │   └── design_system.py  ← drop yours here
│   │   └── data/
│   │       ├── colors.csv
│   │       ├── typography.csv
│   │       └── ...
│   ├── code-reviewer/           ← post-build code review
│   ├── git-commit-writer/       ← clean commits
│   ├── readme-generator/        ← project documentation
│   └── software-architect/      ← architecture artifacts
└── output/                      ← created on first run
    └── <slug>/
        ├── brief.json           ← the answers
        ├── PROMPT.md            ← the master prompt
        ├── llm_response_raw.txt ← Claude's raw response (Mode B only)
        ├── build_meta.json      ← model + elapsed time (Mode B only)
        └── site/                ← Claude's generated website (Mode B only)
            ├── index.html
            ├── styles.css
            └── ...
```

---

## Endpoints

The Python server exposes these for the UI (and useful for scripts and Antigravity actions later):

| Method | Path                       | Purpose                                                              |
|--------|----------------------------|----------------------------------------------------------------------|
| GET    | `/`                        | The visual quiz                                                      |
| GET    | `/api/health`              | Engine + LLM readiness, model name                                  |
| POST   | `/api/build`               | Generate the prompt, save to `output/<slug>/`, return JSON          |
| POST   | `/api/generate`            | Generate the prompt **and** call Claude, write site files          |
| GET    | `/api/briefs`              | List all saved briefs (used by the dashboard)                       |
| GET    | `/api/briefs/<slug>`       | One brief's details: brief, prompt, files                           |
| GET    | `/preview/<slug>/`         | Serve `index.html` of the generated site                            |
| GET    | `/preview/<slug>/path`     | Serve any file in the generated site                                |

---

## What's in the bundle vs. what you provide

This bundle ships with everything except two things from your existing ui-ux-pro-max setup:

- **`skills/ui-ux-pro-max/scripts/design_system.py`** — your design system generator. Drop your existing copy in.
- **Some CSVs** — your `core.py` references `styles.csv`, `landing.csv`, `react-performance.csv`, and `web-interface.csv`. Copy them from your existing data directory into `skills/ui-ux-pro-max/data/`.

The engine **degrades gracefully** if these are missing — the quiz still runs, the brief is still built, the prompt still gets generated. The only thing missing is the engine's specific design system recommendation. The anti-slop audit and general rules still apply. When `pebble_engine.py` starts, it tells you whether the engine loaded cleanly or is running degraded.

---

## How the three layers compose

```
   [INTAKE]              the 14-question quiz
       ↓
   [DATA + REASONING]    ui-ux-pro-max generates a recommendation
       ↓
   [QUALITY FILTER]      no-slop-web audits the recommendation
       ↓
   [MASTER PROMPT]       written to output/<slug>/PROMPT.md
       ↓
   ┌─── BRANCH ───┐
   │              │
[MANUAL]      [AUTO-BUILD]
paste into    Pebble calls Claude,
Antigravity   writes files to disk
       ↓              ↓
   [GENERATED WEBSITE in output/<slug>/site/]
       ↓
   [REVIEW]              code-reviewer + readme-generator + commits
```

The audit is **nuanced** — it doesn't blindly forbid Inter; it forbids Inter when there's no distinctive display companion. A Fraunces + Inter pair passes the audit. An Inter + Roboto pair doesn't. The same applies to other convergence fonts. This means your existing CSV recommendations mostly survive intact; the audit only fires when the engine drifts toward true slop.

---

## Iterating

The highest-leverage edit points:

- **`ui/index.html`** — the `QUESTIONS` array near the top of the `<script>` tag is where you add, remove, or reword the questions. The intake quality compounds — every good question you add raises the floor on every future site.
- **`pebble_engine.py`** — the constants at the top of the audit section (`CONVERGENCE_FONTS`, `ACCEPTABLE_DISPLAY_PAIRS`, `WATCH_STYLES`) are where you tune what the audit flags. Each rule is two or three lines. The `PROMPT_TEMPLATE` constant below it is the full master prompt — edit it and every future site inherits the change.
- **`.env`** — switch models freely. `claude-opus-4-7` for highest quality, `claude-haiku-4-5-20251001` for fastest/cheapest iteration.

The quiz itself is a single HTML file with embedded CSS and JS. No build step, no framework — just edit and refresh.

---

## What's next (when you're ready)

Two obvious extensions, in order of leverage:

1. **Iteration mode** — once a site exists, a "refine" button on the built screen that lets you send a focused diff prompt: "change the hero to X." Pebble parses the LLM's response, replaces just the affected files. Keeps the token cost of changes proportional to the change.
2. **Auto-run post-build skills** — when a site finishes building, automatically trigger the `code-reviewer` skill on the output, surface findings in the built screen. Same for `readme-generator` to write the site's own README into `output/<slug>/site/README.md`.

When you've run it on a real client and want to add any of these, send the change you have in mind and I'll wire it up.
