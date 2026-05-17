"""Setup_needs dependency graph.

The Pebble Plan's `setup_needs` array is the 14-item launch checklist.
Each item carries a `dependencies: [<other_id>, ...]` field so the UI
can render the list as a chain (item B unlocks after item A completes)
rather than a flat list — the No-Code/Builder pattern (#7) from the
Onboarding Pattern Cheat Sheet.

This suite locks in three properties:
1. Every item has a `dependencies` list (may be empty)
2. All referenced ids exist (no dangling refs)
3. No cycles in the dependency graph
"""
from __future__ import annotations

from pebble.plan import _LAUNCH_SETUP_TEMPLATE, build_pebble_plan


def _build_minimal_plan():
    return build_pebble_plan(
        {"business_name": "Test", "business_type": "café"},
        industry_intel=None,
        design_dna=None,
    )


def test_every_setup_need_has_dependencies_field():
    for item in _LAUNCH_SETUP_TEMPLATE:
        assert "dependencies" in item, f"{item['id']!r} missing dependencies field"
        assert isinstance(item["dependencies"], list)


def test_dependencies_only_reference_known_ids():
    known_ids = {item["id"] for item in _LAUNCH_SETUP_TEMPLATE}
    for item in _LAUNCH_SETUP_TEMPLATE:
        for dep in item["dependencies"]:
            assert dep in known_ids, (
                f"{item['id']!r} depends on unknown id {dep!r}"
            )


def test_no_self_dependencies():
    for item in _LAUNCH_SETUP_TEMPLATE:
        assert item["id"] not in item["dependencies"], (
            f"{item['id']!r} cannot depend on itself"
        )


def test_dependency_graph_has_no_cycles():
    """DFS for back-edges. Cycles would break the chain rendering."""
    deps = {item["id"]: list(item["dependencies"]) for item in _LAUNCH_SETUP_TEMPLATE}

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in deps}

    def visit(node: str, path: list[str]) -> None:
        color[node] = GRAY
        for dep in deps[node]:
            if color[dep] == GRAY:
                raise AssertionError(
                    f"cycle detected: {' -> '.join(path + [node, dep])}"
                )
            if color[dep] == WHITE:
                visit(dep, path + [node])
        color[node] = BLACK

    for node in deps:
        if color[node] == WHITE:
            visit(node, [])


def test_plan_output_includes_dependencies():
    """The full Pebble Plan exposes the dependency edges to the UI."""
    plan = _build_minimal_plan()
    assert "setup_needs" in plan
    assert plan["setup_needs"], "setup_needs should not be empty"
    for item in plan["setup_needs"]:
        assert "dependencies" in item
        assert isinstance(item["dependencies"], list)


def test_publish_depends_on_pages_and_hosting():
    """Publish is the terminal node — you can't deploy without pages
    and hosting in place. This anchors the canonical end-of-checklist
    relationship."""
    by_id = {item["id"]: item for item in _LAUNCH_SETUP_TEMPLATE}
    publish_deps = by_id["publish"]["dependencies"]
    assert "pages" in publish_deps
    assert "hosting" in publish_deps


def test_hosting_depends_on_website_address():
    """You can't host without a domain — the natural infra-buildup order."""
    by_id = {item["id"]: item for item in _LAUNCH_SETUP_TEMPLATE}
    assert "website_address" in by_id["hosting"]["dependencies"]


def test_auto_items_dependencies_are_also_auto():
    """If Pebble does X automatically and X depends on Y, then Y must
    also be auto — otherwise X would be blocked by user action.
    Captures the integrity rule that the 'auto' status implies all
    upstream nodes are also handled."""
    by_id = {item["id"]: item for item in _LAUNCH_SETUP_TEMPLATE}
    for item in _LAUNCH_SETUP_TEMPLATE:
        if item["status"] != "auto":
            continue
        for dep in item["dependencies"]:
            dep_item = by_id[dep]
            assert dep_item["status"] == "auto", (
                f"{item['id']!r} is auto but depends on {dep!r} "
                f"which is {dep_item['status']!r} — chain would block"
            )
