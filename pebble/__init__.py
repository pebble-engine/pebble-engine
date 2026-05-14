"""Pebble Engine — internal package.

Modules:
- pebble.log        — structured logger shared by every module (use ``from pebble.log import log``)
- pebble.llm        — LLM client wrappers (Gemini + Anthropic) and provider selection
- pebble.industry   — industries.json loader, fuzzy lookup, LLM research fallback
- pebble.postbuild  — Post-build chain: npm install, next dev, Playwright screenshots
- pebble.server.*   — Extracted HTTP route handlers (currently: pebble.server.build)

The main ``pebble_engine.py`` script re-exports from these modules for backward
compatibility, so the existing test suite and any external callers continue
to work without changes.
"""
