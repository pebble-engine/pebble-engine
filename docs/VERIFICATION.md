# Verification contract

Every agent (Cursor, Claude Code, future hire) must prove claims with commands — never trust chat summaries alone.

## Iron law

```
NO "done" / "deployed" / "passing" WITHOUT VERIFICATION_REPORT.md SHOWING PASS
```

Run the full gate before any handoff:

```bash
python scripts/verify_all.py
```

Marc reads **[VERIFICATION_REPORT.md](../VERIFICATION_REPORT.md)** at repo root (first lines: PASS or FAIL).

## Claim → proof

| Claim | Command | Pass criteria |
|-------|---------|---------------|
| Full gate (required) | `python scripts/verify_all.py` | exit 0; report Status PASS |
| Unit + integration tests | `python -m pytest -q` | exit 0 |
| HTTP route contracts | `python -m pytest tests/test_http_e2e.py -q` | exit 0 |
| Prod API on pebbleapp.ai | `python scripts/verify_prod.py` | exit 0 |
| Preview backend (Railway) | `python scripts/verify_preview_prod.py` | `preview_prod_ready: true` |
| Community APIs | `python scripts/verify_community_prod.py` | exit 0 |
| Launchpad API | `python scripts/verify_launchpad_prod.py` | exit 0 |
| Stripe env (local only) | `python scripts/verify_stripe_setup.py` | exit 0; skipped in `--ci` |
| Handoff has evidence | `python scripts/verify_handoff.py` | exit 0 |

## CI (`--ci` mode)

GitHub Actions runs:

```bash
python scripts/verify_all.py --ci
```

- Runs pytest with CI-safe exclusions (see `pyproject.toml` `markers`)
- Runs prod smoke against `https://www.pebbleapp.ai` (no secrets)
- Skips Stripe local check
- Uploads `VERIFICATION_REPORT.md` as artifact

## Forbidden without evidence

- "should work", "likely fixed", "deployed successfully"
- Handoff without **Evidence** section copied from `VERIFICATION_REPORT.md`
- Commit message implying green tests without running `verify_all.py`

## Handoff

Use [HANDOFF_TEMPLATE.md](../HANDOFF_TEMPLATE.md). Paste the report — do not paraphrase.

## Transitional note (pytest)

CI excludes `@pytest.mark.integration` tests until mocked. Goal: full suite green on `main`. See `pyproject.toml`.
