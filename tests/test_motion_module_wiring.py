"""Regression test that pins ui/v3/lib/motion.ts as the canonical motion
language for the v3 frontend. The actual variant values live in
TypeScript and are verified end-to-end via the plain-Node script at
ui/v3/lib/motion.test.mjs. This test pins the STRUCTURAL side — file
exists, exports the expected tokens, and (in Task 7) is imported by
the phase files.

Two-sided verification keeps the contract honest from both directions
without requiring a JS test runner inside the Python suite.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MOTION_TS = REPO_ROOT / "ui" / "v3" / "lib" / "motion.ts"


def test_motion_module_exists():
    assert MOTION_TS.is_file(), f"Missing: {MOTION_TS}"


def test_motion_exports_durations():
    src = MOTION_TS.read_text(encoding="utf-8")
    for name in ("MICRO", "SHORT", "STANDARD", "SLOW"):
        assert re.search(
            rf"export\s+const\s+{name}\s*=",
            src,
        ), f"motion.ts missing duration export: {name}"


def test_motion_exports_easings():
    src = MOTION_TS.read_text(encoding="utf-8")
    for name in ("EASE_CINEMATIC", "EASE_QUIET"):
        assert re.search(
            rf"export\s+const\s+{name}\s*:",
            src,
        ), f"motion.ts missing easing export: {name}"


def test_motion_exports_variants():
    src = MOTION_TS.read_text(encoding="utf-8")
    for name in ("fadeUp", "phaseVariants", "railStep",
                 "chipDeck", "cardHover", "dropletPulse"):
        assert re.search(
            rf"export\s+const\s+{name}\s*:",
            src,
        ), f"motion.ts missing variant export: {name}"


def test_motion_phase_variants_has_three_states():
    """phaseVariants must declare hidden, visible, and exit so consumers
    can use string variant names (initial="hidden" animate="visible"
    exit="exit") instead of hand-extracting nested keys."""
    src = MOTION_TS.read_text(encoding="utf-8")
    # Match the phaseVariants object body and check all three keys appear.
    block = re.search(
        r"export\s+const\s+phaseVariants\s*:[^=]*=\s*\{(.*?)^\};",
        src,
        re.DOTALL | re.MULTILINE,
    )
    assert block, "phaseVariants object body not found"
    body = block.group(1)
    for key in ("hidden", "visible", "exit"):
        assert re.search(rf"\b{key}\s*:", body), \
            f"phaseVariants missing '{key}' state key"


def test_motion_phase_variants_replaces_old_exports():
    """Round 2 cleanup: phaseEnter + phaseExit were merged into phaseVariants.
    Make sure the legacy names are gone so no caller silently picks them up."""
    src = MOTION_TS.read_text(encoding="utf-8")
    for legacy in ("phaseEnter", "phaseExit"):
        assert not re.search(rf"export\s+const\s+{legacy}\s*:", src), \
            f"legacy export `{legacy}` should have been removed"


def test_motion_exports_reduced_motion_helper():
    src = MOTION_TS.read_text(encoding="utf-8")
    assert "export function prefersReducedMotion" in src
    assert "export function withReducedMotion" in src


PHASE_FILES = [
    REPO_ROOT / "ui" / "v3" / "components" / "workspace-shell.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "welcome-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "idea-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "plan-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "draft-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "edit-phase.tsx",
    REPO_ROOT / "ui" / "v3" / "components" / "phases" / "publish-phase.tsx",
]


@pytest.mark.parametrize("phase_file", PHASE_FILES, ids=lambda p: p.name)
def test_phase_file_imports_from_motion_module(phase_file):
    src = phase_file.read_text(encoding="utf-8")
    assert re.search(
        r"from\s+['\"]@/lib/motion['\"]",
        src,
    ), f"{phase_file.name} should import from @/lib/motion"


PROJECT_NAME_LAYOUT_ID_FILES = [
    REPO_ROOT / "ui" / "v3" / "components" / "top-nav.tsx",
]


@pytest.mark.parametrize(
    "endpoint_file", PROJECT_NAME_LAYOUT_ID_FILES, ids=lambda p: p.name
)
def test_project_name_layout_id_is_wired(endpoint_file):
    """The project-name slot in the TopNav declares `layoutId="project-name"`
    so framer-motion can morph it into place when arriving from any future
    surface that mounts a peer with the same id. The welcome hero used to
    carry the source kicker but it was removed at Marc's request — the
    morph is now graceful (no source = no morph; destination just appears)."""
    src = endpoint_file.read_text(encoding="utf-8")
    assert re.search(
        r'layoutId\s*=\s*["\']project-name["\']',
        src,
    ), f"{endpoint_file.name} must declare layoutId=\"project-name\" for the morph"


def test_workspace_shell_wraps_in_motion_config_reduced_motion():
    """layoutId / shared-element morphs bypass the withReducedMotion wrapper
    (it only operates on Variants). The shell must wrap its tree in
    `<MotionConfig reducedMotion="user">` so framer honors the OS pref for
    those animations too."""
    shell = REPO_ROOT / "ui" / "v3" / "components" / "workspace-shell.tsx"
    src = shell.read_text(encoding="utf-8")
    assert "MotionConfig" in src, (
        "workspace-shell.tsx must import MotionConfig from framer-motion"
    )
    assert re.search(
        r'reducedMotion\s*=\s*["\']user["\']',
        src,
    ), 'workspace-shell.tsx must set reducedMotion="user" on MotionConfig'


@pytest.mark.parametrize("phase_file", PHASE_FILES, ids=lambda p: p.name)
def test_named_variants_pair_with_with_reduced_motion(phase_file):
    """Round 2 cleanup (b): wherever a phase file uses a named variant
    (`variants={someConst}`, NOT inline `variants={{ ... }}`), it must
    also call `withReducedMotion` at least once, so the OS reduce-motion
    preference is honored consumer-side. The motion module exports
    bare Variants — consumers opt into the reduced-motion collapse.
    """
    src = phase_file.read_text(encoding="utf-8")
    # `variants={ident}` — single identifier inside the braces.
    named_uses = re.findall(r"variants=\{(\w+)\}", src)
    if not named_uses:
        return  # File only uses inline variants, or none at all.
    assert "withReducedMotion(" in src, (
        f"{phase_file.name} uses named variants {sorted(set(named_uses))} "
        "but never calls withReducedMotion()"
    )
    assert re.search(r"\bwithReducedMotion\b", src), (
        f"{phase_file.name} must import withReducedMotion from @/lib/motion"
    )
