"""Pebble Engine — internal package.

Modules:
- pebble.llm        — LLM client wrappers (Gemini + Anthropic) and provider selection
- pebble.postbuild  — Post-build chain: npm install, next dev, Playwright screenshots
- pebble.industry   — industries.json loader, fuzzy lookup, LLM research fallback

The main `pebble_engine.py` script re-exports from these modules for backward
compatibility, so the existing test suite and any external callers continue
to work without changes.
"""
