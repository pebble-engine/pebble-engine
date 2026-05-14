# Repair Corpus

A regression library of historical broken builds. Every PR touching
`pebble.evals.checks` or `pebble.repair` should be tested against this
corpus to prove it still produces the expected lift on each case.

## Per-case layout

```
<case-slug>/
  brief.json              — the user's intake (frozen)
  site/                   — the broken site as the LLM emitted it
  expected_failures.json  — { "failing_checks": ["...", ...],
                              "baseline_score": "N/M" }
  canned_response.txt     — the <pebble-file> blocks a corrected LLM should produce
  expected_repair.json    — { "final_score": "N/M",
                              "files_written": ["..."],
                              "kept": true }
```

A test in `tests/test_repair_corpus.py` walks the directory, runs each case
through `repair_build()` with a `FakeClient` returning `canned_response.txt`,
and asserts the loop reaches the expected final state. This way the regression
library never costs LLM tokens to run.

## Adding a new case

1. Pick a real broken build from `output/<slug>/` you'd want to never regress.
2. Copy `output/<slug>/brief.json` and `output/<slug>/site/` into a new case
   directory here. Sanitize any secrets (none expected in briefs).
3. Run `python -m pebble.evals <slug> --skip-compile`. Note the failing checks.
4. Author the `canned_response.txt` — a `<pebble-file>` block per file the
   repair should write. Use realistic content.
5. Run `python -m pebble.repair <slug>` against your local working copy with
   the canned response substituted in (or rely on the test runner to verify).
6. Capture the expected final score and add the case files.

## Existing cases

- `missing-page/` — page.tsx was never generated; site is dead on arrival.
  Mirrors the 2026-05-13 sentinel-hvac-e2e-2 incident.
