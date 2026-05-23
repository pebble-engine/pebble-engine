"""Morning brief — Tier-2 autonomy: read-only summary of what happened overnight.

Marc's vision (2026-05-23): "Boot up the computer in the morning and get
complete breakdowns of what happened in plain language." This module is
v1 of that — a single Python script that gathers data from local sources
+ optional external APIs, then renders a Markdown brief.

Tier-2 boundary:
    Reads everything. Writes nothing. Recommends fixes via prose, never
    auto-applies. Marc reviews + acts. The brief is information, not
    action. (See docs/MORNING_BRIEF.md for the full design discussion.)

Data sources, by tier of integration cost:

    LOCAL (free, always available — what v1 ships with)
        - engine.err.log         → recent ERROR/WARN lines
        - engine.log             → boot history, build cadence
        - output/<slug>/         → projects, build_meta.json, brief.json
        - output/.engagement/    → per-user event timelines (T17)
        - output/.users/<uid>/   → subscription state + email_drip
        - git log / git status   → commits since last brief, dirty work

    EXTERNAL (needs a PAT in .env — opt-in)
        - SENTRY_PAT             → unresolved issues since last brief
        - PEBBLE_SUPABASE_PAT    → advisor changes since last brief

The external paths gracefully no-op when their PATs are missing — the
brief just notes "(Sentry: skipped, no SENTRY_PAT)" so Marc sees the
gap without the script crashing.

Usage:
    python -m pebble.morning_brief                  # print to stdout
    python -m pebble.morning_brief --out brief.md   # write file
    python -m pebble.morning_brief --json           # machine-readable

Future (NOT in v1, see design doc):
    - Schedule via scheduled-tasks MCP or Hermes cron
    - Deliver via Telegram (Hermes), Slack webhook, or email (Resend)
    - LLM pass to turn the structured brief into prose
    - Auto-PR creation for clear-cut bug patterns (Tier-2 power feature)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Paths + config
# ---------------------------------------------------------------------------

# Default to the repo root inferred from this file's location. The CLI can
# override via --root (or env var PEBBLE_BRIEF_ROOT) so the brief can run
# from a git worktree but report on the base repo's output/ + logs.
PROJECT_ROOT = Path(
    os.environ.get("PEBBLE_BRIEF_ROOT")
    or Path(__file__).parent.parent
).resolve()
OUTPUT_DIR   = PROJECT_ROOT / "output"
ENGINE_LOG   = PROJECT_ROOT / "engine.log"
ENGINE_ERR   = PROJECT_ROOT / "engine.err.log"


def _set_root(new_root: Path) -> None:
    """Repoint module-level paths at *new_root*. CLI calls this when
    --root is provided so every section sees the override."""
    global PROJECT_ROOT, OUTPUT_DIR, ENGINE_LOG, ENGINE_ERR
    PROJECT_ROOT = new_root.resolve()
    OUTPUT_DIR   = PROJECT_ROOT / "output"
    ENGINE_LOG   = PROJECT_ROOT / "engine.log"
    ENGINE_ERR   = PROJECT_ROOT / "engine.err.log"

# Look-back window. 24h matches "what happened overnight"; tunable from CLI.
DEFAULT_WINDOW_HOURS = 24


# ---------------------------------------------------------------------------
# Tiny structured types
# ---------------------------------------------------------------------------

@dataclass
class Section:
    """One section of the brief — title, severity, prose body."""
    title:    str
    severity: str               # "ok" | "info" | "warn" | "critical"
    lines:    list[str] = field(default_factory=list)
    # Free-form metadata for the --json output, ignored in markdown.
    meta:     dict = field(default_factory=dict)


@dataclass
class Brief:
    generated_at: str
    window_hours: int
    sections:     list[Section] = field(default_factory=list)

    @property
    def severity(self) -> str:
        # Worst-case rollup so the title can render an at-a-glance signal.
        order = {"ok": 0, "info": 1, "warn": 2, "critical": 3}
        worst = max((order[s.severity] for s in self.sections), default=0)
        return next(k for k, v in order.items() if v == worst)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _since(hours: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=hours)


def _parse_iso(value: str) -> Optional[datetime]:
    """Best-effort ISO-8601 parse; returns None on garbage."""
    if not value:
        return None
    try:
        # Python's fromisoformat handles ±HH:MM offsets in 3.11+. The "+00:00"
        # vs "Z" distinction matters: normalize Z to +00:00 first.
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _safe_run(cmd: list[str], cwd: Optional[Path] = None,
              timeout: int = 5) -> Optional[str]:
    """Run a shell command, capturing stdout; return None on any failure
    so caller can degrade gracefully instead of crashing the whole brief."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd or PROJECT_ROOT, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Section: engine logs (engine.err.log + engine.log)
# ---------------------------------------------------------------------------

# Match lines we'd want to surface from engine.err.log. Conservative —
# false-positive a normal stack trace is better than missing a real error.
_ERR_PATTERNS = (
    re.compile(r"\bERROR\b",      re.IGNORECASE),
    re.compile(r"\bTraceback\b"),
    re.compile(r"\bException\b"),
    re.compile(r"\bCRITICAL\b",   re.IGNORECASE),
)
_WARN_PATTERNS = (
    re.compile(r"\bWARN(?:ING)?\b", re.IGNORECASE),
)

# Patterns that look like recurring noise we don't need surfaced every
# morning. Marc can extend this list as patterns emerge.
_NOISE_PATTERNS = (
    re.compile(r"DeprecationWarning"),  # third-party deprecations
    re.compile(r"ResourceWarning"),
)


def section_engine_log(window_hours: int) -> Section:
    """Tail engine.err.log + classify recent lines.

    We can't trust the per-line timestamps because the engine doesn't
    timestamp every line. So we use a heuristic: read the last N lines
    (cheap), classify each, and bucket by pattern. The window_hours value
    is reported as context, not used for filtering — that's an honest
    limitation surfaced in the brief itself.
    """
    if not ENGINE_ERR.exists():
        return Section(
            title="Engine errors", severity="info",
            lines=["(no engine.err.log yet — engine never started, or fresh checkout)"],
        )

    # Cap at last 5MB to bound memory on weeks-old logs.
    # If the file is smaller than the cap, just read the whole thing —
    # `seek(-bytes, 2)` errors on small files because the negative
    # offset from end would land before byte 0.
    size = ENGINE_ERR.stat().st_size
    cap = 5 * 1024 * 1024
    with ENGINE_ERR.open("rb") as f:
        if size > cap:
            f.seek(-cap, 2)
        tail = f.read().decode("utf-8", errors="replace")

    errors, warnings, noise = [], [], []
    for line in tail.splitlines():
        if any(p.search(line) for p in _NOISE_PATTERNS):
            noise.append(line)
            continue
        if any(p.search(line) for p in _ERR_PATTERNS):
            errors.append(line)
        elif any(p.search(line) for p in _WARN_PATTERNS):
            warnings.append(line)

    severity = (
        "critical" if errors    else
        "warn"     if warnings  else
        "ok"
    )

    lines: list[str] = []
    if errors:
        lines.append(f"**{len(errors)} error line(s)** — top 5 most recent:")
        for ln in errors[-5:]:
            lines.append(f"    `{ln.strip()[:200]}`")
    if warnings:
        lines.append(f"\n**{len(warnings)} warning(s)** — top 3 most recent:")
        for ln in warnings[-3:]:
            lines.append(f"    `{ln.strip()[:200]}`")
    if noise:
        lines.append(f"\n_({len(noise)} suppressed noise lines: deprecation / resource warnings)_")
    if not errors and not warnings:
        lines.append("✓ No errors or warnings in the last log scan.")

    lines.append(
        f"\n_Note: lines aren't timestamped, so the {window_hours}h "
        "window is reported as context — not used for filtering. "
        "Last 5MB of engine.err.log scanned._"
    )
    return Section(
        title="Engine errors", severity=severity, lines=lines,
        meta={"error_count": len(errors), "warn_count": len(warnings)},
    )


# ---------------------------------------------------------------------------
# Section: git activity
# ---------------------------------------------------------------------------

def section_git(window_hours: int) -> Section:
    """Commits in the window, branches with unpushed work, dirty files."""
    lines: list[str] = []
    severity = "ok"

    # Recent commits — git log handles the time filtering natively.
    since = _since(window_hours).isoformat()
    log_out = _safe_run([
        "git", "log", f"--since={since}", "--oneline", "--no-merges",
    ])
    if log_out is not None:
        commits = [ln for ln in log_out.splitlines() if ln.strip()]
        if commits:
            lines.append(f"**{len(commits)} commit(s)** in the last {window_hours}h:")
            for c in commits[:8]:
                lines.append(f"    `{c}`")
            if len(commits) > 8:
                lines.append(f"    _… {len(commits) - 8} more_")
        else:
            lines.append(f"(no commits in the last {window_hours}h)")
    else:
        lines.append("_(git log failed — not a repo, or git not installed)_")

    # Uncommitted work — surface lightly; tracked-file mods are warning, untracked is info.
    status_out = _safe_run(["git", "status", "--porcelain"])
    if status_out is not None:
        dirty = [ln for ln in status_out.splitlines() if ln.strip()]
        tracked_mods = [ln for ln in dirty if not ln.startswith("??")]
        untracked    = [ln for ln in dirty if ln.startswith("??")]
        if tracked_mods or untracked:
            lines.append("\n**Uncommitted in worktree:**")
            if tracked_mods:
                lines.append(f"    {len(tracked_mods)} modified tracked file(s) — `git status` to see")
                severity = "warn" if severity == "ok" else severity
            if untracked:
                lines.append(f"    {len(untracked)} untracked file(s) — new work not yet `git add`'d")

    # Unpushed commits (current branch). Best effort — silently skip if remote
    # tracking isn't set up.
    ahead_out = _safe_run([
        "git", "rev-list", "--count", "@{upstream}..HEAD",
    ])
    if ahead_out and ahead_out.strip().isdigit():
        ahead = int(ahead_out.strip())
        if ahead:
            lines.append(f"\n**{ahead} unpushed commit(s)** on current branch — `git push` when ready.")

    return Section(title="Code activity (git)", severity=severity, lines=lines)


# ---------------------------------------------------------------------------
# Section: build / cost activity
# ---------------------------------------------------------------------------

def section_builds(window_hours: int) -> Section:
    """Recent builds + cost, scanned from output/<slug>/build_meta.json."""
    if not OUTPUT_DIR.exists():
        return Section(
            title="Build activity", severity="info",
            lines=["(no output/ directory yet — no builds ever run)"],
        )

    since = _since(window_hours)
    recent: list[dict] = []
    for project_dir in OUTPUT_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        meta_path = project_dir / "build_meta.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        built_at = _parse_iso(meta.get("built_at", ""))
        if not built_at:
            continue
        # Make naive datetimes UTC so comparison works.
        if built_at.tzinfo is None:
            built_at = built_at.replace(tzinfo=timezone.utc)
        if built_at < since:
            continue
        recent.append({
            "slug":     project_dir.name,
            "built_at": built_at.isoformat(),
            "model":    meta.get("model", "?"),
            "cost":     float(meta.get("estimated_cost_usd", 0) or 0),
            "billable": bool(meta.get("billable", True)),
            "tokens":   (meta.get("tokens_used") or {}),
        })

    lines: list[str] = []
    total_cost = sum(r["cost"] for r in recent)
    billable_cost = sum(r["cost"] for r in recent if r["billable"])
    total_in  = sum(r["tokens"].get("input", 0)  for r in recent)
    total_out = sum(r["tokens"].get("output", 0) for r in recent)

    if recent:
        lines.append(f"**{len(recent)} build(s)** in the last {window_hours}h")
        lines.append(f"- Total cost: **${total_cost:.4f}** (${billable_cost:.4f} billable)")
        lines.append(f"- Tokens: {total_in:,} in / {total_out:,} out")
        lines.append("- Top 5 by cost:")
        for r in sorted(recent, key=lambda x: -x["cost"])[:5]:
            badge = "🪙" if r["billable"] else "✨"
            lines.append(f"    {badge} `{r['slug']}` — ${r['cost']:.4f} ({r['model']})")
    else:
        lines.append(f"(no builds in the last {window_hours}h)")

    severity = "info" if recent else "ok"
    return Section(
        title="Build activity", severity=severity, lines=lines,
        meta={"count": len(recent), "total_cost_usd": round(total_cost, 6)},
    )


# ---------------------------------------------------------------------------
# Section: user engagement
# ---------------------------------------------------------------------------

def section_engagement(window_hours: int) -> Section:
    """Per-user event activity from output/.engagement/<uid>.jsonl."""
    eng_dir = OUTPUT_DIR / ".engagement"
    if not eng_dir.exists():
        return Section(
            title="User engagement", severity="info",
            lines=["(no engagement data yet — output/.engagement/ doesn't exist)"],
        )

    since = _since(window_hours)
    per_user: dict[str, Counter] = defaultdict(Counter)
    for log_file in eng_dir.glob("*.jsonl"):
        uid = log_file.stem
        try:
            for raw in log_file.read_text(encoding="utf-8").splitlines():
                if not raw.strip():
                    continue
                try:
                    rec = json.loads(raw)
                except Exception:
                    continue
                ts = _parse_iso(rec.get("timestamp", ""))
                if not ts or ts < since:
                    continue
                per_user[uid][rec.get("event", "?")] += 1
        except Exception:
            continue

    lines: list[str] = []
    if per_user:
        lines.append(f"**{len(per_user)} active user(s)** in the last {window_hours}h")
        for uid, events in sorted(per_user.items(), key=lambda kv: -sum(kv[1].values()))[:5]:
            total = sum(events.values())
            top = ", ".join(f"{k}×{v}" for k, v in events.most_common(3))
            lines.append(f"    - `{uid[:8]}…` — {total} events ({top})")
    else:
        lines.append(f"(no engagement events in the last {window_hours}h)")

    return Section(
        title="User engagement", severity="info", lines=lines,
        meta={"active_users": len(per_user)},
    )


# ---------------------------------------------------------------------------
# Section: subscriptions
# ---------------------------------------------------------------------------

def section_subscriptions(_window_hours: int) -> Section:
    """Snapshot of all current subscriptions across users."""
    users_dir = OUTPUT_DIR / ".users"
    if not users_dir.exists():
        return Section(
            title="Subscriptions", severity="info",
            lines=["(no .users dir yet — no signups via the production webhook)"],
        )

    plans: Counter = Counter()
    statuses: Counter = Counter()
    pending_deletion = 0
    for user_dir in users_dir.iterdir():
        if not user_dir.is_dir():
            continue
        if (user_dir / "pending_deletion.json").exists():
            pending_deletion += 1
        sub_path = user_dir / "subscription.json"
        if sub_path.exists():
            try:
                sub = json.loads(sub_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            plans[sub.get("plan") or "(none)"] += 1
            statuses[sub.get("status") or "(unknown)"] += 1

    lines: list[str] = []
    if plans:
        lines.append("**Plans:** " + ", ".join(f"{p}×{c}" for p, c in plans.most_common()))
    if statuses:
        lines.append("**Statuses:** " + ", ".join(f"{s}×{c}" for s, c in statuses.most_common()))
    if pending_deletion:
        lines.append(f"**⚠ {pending_deletion} account(s) pending deletion** — review the cooling-off queue")
    if not plans and not statuses and not pending_deletion:
        lines.append("(no subscription state for any user)")

    return Section(title="Subscriptions", severity="info", lines=lines)


# ---------------------------------------------------------------------------
# Section: Sentry (stub — needs SENTRY_PAT)
# ---------------------------------------------------------------------------

_SENTRY_ORG_SLUG = "pebble-6q"
_SENTRY_API_BASE = "https://us.sentry.io/api/0"


def section_sentry(window_hours: int) -> Section:
    """Unresolved Sentry issues from the window.

    Why a PAT instead of the OAuth MCP? The MCP is bound to a Claude
    Code session and can't be called by a standalone Python cron job.
    Marc generates a Personal Auth Token at
    https://pebble-6q.sentry.io/settings/account/api/auth-tokens/
    with `org:read`, `project:read`, `event:read` scopes. Add to .env
    as SENTRY_PAT=<token> and the next run picks it up.
    """
    pat = os.environ.get("SENTRY_PAT", "").strip()
    if not pat:
        return Section(
            title="Sentry errors", severity="info",
            lines=[
                "_skipped — SENTRY_PAT not set in .env_",
                "",
                "To enable: generate a Personal Auth Token at "
                "https://pebble-6q.sentry.io/settings/account/api/auth-tokens/ "
                "with scopes: `org:read`, `project:read`, `event:read`. Add "
                "to `.env` as `SENTRY_PAT=<token>` and re-run.",
            ],
        )

    # Translate hours → Sentry's statsPeriod format: 24h / 7d / 30d
    if   window_hours <= 24:   stats_period = f"{window_hours}h"
    elif window_hours <= 168:  stats_period = f"{window_hours // 24}d"
    else:                      stats_period = "7d"

    import urllib.parse
    import urllib.request

    url = (f"{_SENTRY_API_BASE}/organizations/{_SENTRY_ORG_SLUG}/issues/"
           f"?{urllib.parse.urlencode({'query': 'is:unresolved', 'statsPeriod': stats_period, 'limit': 25})}")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {pat}",
        "User-Agent":    "pebble-morning-brief/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            issues = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return Section(
            title="Sentry errors", severity="warn",
            lines=[f"_query failed: {e!r}_",
                   "_(check SENTRY_PAT validity + scopes at "
                   "https://pebble-6q.sentry.io/settings/account/api/auth-tokens/)_"],
        )

    if not issues:
        return Section(
            title="Sentry errors", severity="ok",
            lines=[f"✓ 0 unresolved issues across all projects in the last {stats_period}."],
        )

    # Bucket by project + level so a flood of one error doesn't drown
    # everything else in the summary.
    by_project: dict[str, list[dict]] = defaultdict(list)
    for issue in issues:
        proj = (issue.get("project") or {}).get("slug") or "?"
        by_project[proj].append(issue)

    lines = [f"**{len(issues)} unresolved issue(s)** across {len(by_project)} project(s) in the last {stats_period}:"]
    for proj, project_issues in sorted(by_project.items()):
        lines.append(f"\n**`{proj}`** ({len(project_issues)} issue(s)):")
        for issue in sorted(project_issues, key=lambda i: -int(i.get("count", 0) or 0))[:5]:
            count = issue.get("count", "?")
            users = issue.get("userCount", 0)
            title = (issue.get("title") or "(no title)")[:100]
            level = issue.get("level", "?")
            user_str = f", {users} user(s)" if users else ""
            lines.append(f"    - [{level}] `{title}` — {count} event(s){user_str}")
            permalink = issue.get("permalink")
            if permalink:
                lines.append(f"      {permalink}")

    # Severity: critical if any error-level issue affects ≥1 user, warn otherwise.
    has_user_impact = any(
        (i.get("level") in {"error", "fatal"}) and int(i.get("userCount", 0) or 0) > 0
        for i in issues
    )
    severity = "critical" if has_user_impact else "warn"
    return Section(
        title="Sentry errors", severity=severity, lines=lines,
        meta={"total_issues": len(issues), "projects": list(by_project.keys())},
    )


# ---------------------------------------------------------------------------
# Section: Supabase advisors (stub — needs PEBBLE_SUPABASE_PAT)
# ---------------------------------------------------------------------------

_SUPABASE_PROJECT_REF = "tarobysyjnmblvpznmdq"  # Pebble's Supabase project
_SUPABASE_API_BASE    = "https://api.supabase.com/v1"


def section_supabase_advisors(_window_hours: int) -> Section:
    """Current Supabase advisor findings (security + performance).

    Doesn't diff against yesterday yet — that needs a persistent
    snapshot file; v2 work. v1 just reports the current state, which
    is still useful for "are we good?" at-a-glance.

    Marc generates a PAT at https://supabase.com/dashboard/account/tokens
    (no scope picker — PATs are full account scope). Add to .env as
    PEBBLE_SUPABASE_PAT.
    """
    pat = os.environ.get("PEBBLE_SUPABASE_PAT", "").strip()
    if not pat:
        return Section(
            title="Supabase advisors", severity="info",
            lines=[
                "_skipped — PEBBLE_SUPABASE_PAT not set in .env_",
                "",
                "To enable: generate a Personal Access Token at "
                "https://supabase.com/dashboard/account/tokens. Add to "
                "`.env` as `PEBBLE_SUPABASE_PAT=<token>`.",
            ],
        )

    import urllib.request

    def _fetch(kind: str) -> list[dict]:
        url = f"{_SUPABASE_API_BASE}/projects/{_SUPABASE_PROJECT_REF}/advisors/{kind}"
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {pat}",
            "User-Agent":    "pebble-morning-brief/1.0",
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        # Supabase advisor responses wrap the array under "lints"
        return payload.get("lints") or payload if isinstance(payload, dict) else payload

    try:
        sec  = _fetch("security")
        perf = _fetch("performance")
    except Exception as e:
        return Section(
            title="Supabase advisors", severity="warn",
            lines=[f"_query failed: {e!r}_",
                   "_(check PEBBLE_SUPABASE_PAT at "
                   "https://supabase.com/dashboard/account/tokens)_"],
        )

    # Level buckets per Supabase advisor docs: INFO / WARN / ERROR
    by_level: Counter = Counter()
    for finding in (sec or []) + (perf or []):
        by_level[finding.get("level") or "?"] += 1

    lines = []
    if not sec and not perf:
        lines.append("✓ No advisor findings — security AND performance clean.")
        severity = "ok"
    else:
        lines.append(
            f"**{len(sec)} security finding(s)**, "
            f"**{len(perf)} performance finding(s)** currently open."
        )
        if by_level:
            lines.append("By level: " + ", ".join(f"{lvl}×{n}" for lvl, n in by_level.most_common()))
        if sec:
            lines.append("\n**Top 5 security findings:**")
            for f in sec[:5]:
                title = f.get("title") or f.get("name") or "(no title)"
                lines.append(f"    - [{f.get('level', '?')}] `{title}`")
        severity = "warn" if by_level.get("ERROR", 0) else "info"

    return Section(
        title="Supabase advisors", severity=severity, lines=lines,
        meta={"security_count": len(sec), "performance_count": len(perf)},
    )


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

_SEVERITY_BADGE = {
    "ok":       "🟢",
    "info":     "🔵",
    "warn":     "🟡",
    "critical": "🔴",
}


def render_markdown(brief: Brief) -> str:
    badge   = _SEVERITY_BADGE[brief.severity]
    ts_iso  = brief.generated_at
    out = [
        f"# {badge} Pebble morning brief — {ts_iso[:10]}",
        "",
        f"_Generated at {ts_iso} · window: last {brief.window_hours}h · "
        f"overall severity: **{brief.severity}**_",
        "",
    ]
    for sec in brief.sections:
        sev_badge = _SEVERITY_BADGE[sec.severity]
        out.append(f"## {sev_badge} {sec.title}")
        out.append("")
        out.extend(sec.lines)
        out.append("")
    out.append("---")
    out.append("_Generated by `python -m pebble.morning_brief`. "
               "Design doc: `docs/MORNING_BRIEF.md`._")
    return "\n".join(out)


def render_json(brief: Brief) -> str:
    return json.dumps(asdict(brief), indent=2)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

# Order matters — most-actionable on top so a quick skim catches the
# critical signal first.
_SECTION_BUILDERS = [
    section_engine_log,
    section_sentry,
    section_supabase_advisors,
    section_git,
    section_builds,
    section_engagement,
    section_subscriptions,
]


def build_brief(window_hours: int = DEFAULT_WINDOW_HOURS) -> Brief:
    """Compose the brief by calling every section builder in order.

    Wrap each builder in try/except so a bug in one section never blocks
    the rest — Tier-2 reliability principle: partial brief beats no brief.
    """
    brief = Brief(
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        window_hours=window_hours,
    )
    for builder in _SECTION_BUILDERS:
        try:
            brief.sections.append(builder(window_hours))
        except Exception as e:
            brief.sections.append(Section(
                title=f"{builder.__name__} (FAILED)", severity="warn",
                lines=[f"_section builder crashed: {e!r}_",
                       "_check the script — every other section is still good_"],
            ))
    return brief


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli() -> int:
    # Windows console defaults to cp1252, which can't encode the emoji
    # severity badges. Force stdout to UTF-8 so the script works on every
    # platform without surprising the user. No-op on macOS / Linux.
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description="Pebble morning brief — read-only overnight summary.",
    )
    parser.add_argument("--hours", type=int, default=DEFAULT_WINDOW_HOURS,
                        help=f"look-back window in hours (default: {DEFAULT_WINDOW_HOURS})")
    parser.add_argument("--root", type=str, default=None,
                        help="repo root to scan (default: script's parent dir, or "
                             "$PEBBLE_BRIEF_ROOT if set). Use when running a "
                             "worktree-installed copy against the base repo's "
                             "output/ + engine logs.")
    parser.add_argument("--out", type=str, default=None,
                        help="write to this file instead of stdout")
    parser.add_argument("--json", action="store_true",
                        help="emit structured JSON instead of Markdown")
    args = parser.parse_args()

    if args.root:
        _set_root(Path(args.root))

    brief = build_brief(window_hours=args.hours)
    output = render_json(brief) if args.json else render_markdown(brief)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
