"""Post-build patch for the generated next.config.mjs (Phase 20c, 2026-05-20).

Why this exists
---------------
Next.js 15.5+ warns on every dev request from 127.0.0.1 to /_next/* that the
origin is not in the build's ``allowedDevOrigins`` list, and a future major
version will *block* such requests outright. Marc surfaced this warning in
the 2026-05-20 mechanic-shop-inqueens preview terminal:

    ⚠ Cross origin request detected from 127.0.0.1 to /_next/* resource.
    In a future major version of Next.js, you will need to explicitly
    configure "allowedDevOrigins" in next.config to allow this.

The generated config Qwen emits is the minimal::

    /** @type {import('next').NextConfig} */
    const nextConfig = {};
    export default nextConfig;

which means every preview triggers the warning. Rather than rely on the
LLM remembering to add the field (which the existing prompt directives
already failed to enforce), this module patches the file after the LLM
output has been written — idempotent, regex-narrow, no risk to the rest of
the config.
"""
from __future__ import annotations

import re
from pathlib import Path

# The dev origins we want allowed. Both 127.0.0.1 and localhost cover the
# usual local-dev surfaces; '*.local' supports mDNS / .local hostnames the
# host machine resolves (rare but real, e.g. on iPad simulator testing).
_ALLOWED_ORIGINS_LIST = "['127.0.0.1', 'localhost', '*.local']"

# The line we insert. Two-space indent matches the template's style.
_INSERT_LINE = f"  allowedDevOrigins: {_ALLOWED_ORIGINS_LIST},"

# Match the `const nextConfig = {` opener. Tolerant of newlines + whitespace
# (some hand-styled configs span multiple lines).
_NEXT_CONFIG_OPEN_RE = re.compile(r"(const\s+nextConfig\s*=\s*\{)")


def ensure_allowed_dev_origins(config_path: Path) -> bool:
    """Inject ``allowedDevOrigins`` into ``next.config.mjs`` if missing.

    Returns ``True`` when the file was patched, ``False`` otherwise (no
    file, already patched, or no recognizable ``const nextConfig`` opener
    — e.g. if the LLM wrote a `module.exports` style config).

    Idempotent: a second call on an already-patched file is a no-op.
    Side-effect: writes UTF-8 with the existing line ending convention
    preserved (text mode, default).
    """
    if not config_path.exists():
        return False
    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError:
        return False

    # Idempotency check — already patched
    if "allowedDevOrigins" in text:
        return False

    new_text, n = _NEXT_CONFIG_OPEN_RE.subn(
        r"\1\n" + _INSERT_LINE,
        text,
        count=1,
    )
    if n == 0:
        return False

    try:
        config_path.write_text(new_text, encoding="utf-8")
        return True
    except OSError:
        return False
