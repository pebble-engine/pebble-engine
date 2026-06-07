"""Tests for pebble.knowledge — durable per-project + per-account
"about your business" context (P1). Pure-function core; storage + render."""
from __future__ import annotations

from pathlib import Path

from pebble import knowledge as k


def test_project_knowledge_reads_brief_field():
    assert k.project_knowledge({"business_knowledge": "We close Sundays."}) == "We close Sundays."


def test_project_knowledge_blank_when_absent():
    assert k.project_knowledge({}) == ""
    assert k.project_knowledge({"business_knowledge": None}) == ""


def test_knowledge_block_empty_when_no_knowledge():
    assert k.render_knowledge_block(project="", account="") == ""


def test_knowledge_block_includes_both_scopes_labeled():
    out = k.render_knowledge_block(project="Closed Sundays.", account="Brand voice: warm.")
    assert "ABOUT THIS BUSINESS" in out
    assert "Closed Sundays." in out
    assert "Brand voice: warm." in out


def test_knowledge_block_truncates_overlong_input():
    out = k.render_knowledge_block(project="x" * 10000, account="")
    assert len(out) <= k.MAX_BLOCK_CHARS + 200  # block + header overhead


def test_sanitize_strips_braces_for_strformat_safety():
    # build_prompt renders via str.format — knowledge must not inject { }
    out = k.render_knowledge_block(project="a {b} c", account="")
    assert "{" not in out
    assert "}" not in out


def test_account_knowledge_round_trip(tmp_path: Path):
    uid = "user-123"
    assert k.load_account_knowledge(tmp_path, uid) == ""
    k.save_account_knowledge(tmp_path, uid, "  Always mention financing.  ")
    assert k.load_account_knowledge(tmp_path, uid) == "Always mention financing."


def test_account_knowledge_blank_uid_is_safe(tmp_path: Path):
    assert k.load_account_knowledge(tmp_path, "") == ""
