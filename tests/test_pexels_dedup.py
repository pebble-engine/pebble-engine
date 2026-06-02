"""Tests for Pexels dedup: distinct photos per query and across sections.

Part of the fix for the "same popular photo repeated across a services grid"
bug discovered during a real build verification (2026-06-01).
"""
import pebble.pexels_resolver as pr


def test_distinct_queries_get_distinct_photos_when_top_hit_collides(monkeypatch):
    # Both queries' top hit is the SAME url; dedup must push the 2nd to its #2.
    catalog = {
        "water heater plumber": ["https://img/A.jpg", "https://img/B.jpg"],
        "leak detection plumber": ["https://img/A.jpg", "https://img/C.jpg"],
    }
    monkeypatch.setattr(pr, "_fetch_pexels_image_urls",
                        lambda q, n=15: catalog.get(q, []))
    src = (
        'src="water heater plumber"\n'
        'src="leak detection plumber"\n'
    )
    out = pr.resolve_pexels_tags(src)
    assert 'src="https://img/A.jpg"' in out
    # second query must NOT also be A — deduped to C (its first unused)
    assert 'src="https://img/C.jpg"' in out
    assert out.count('https://img/A.jpg') == 1


def test_used_set_threads_across_calls(monkeypatch):
    catalog = {"q1": ["https://img/A.jpg", "https://img/B.jpg"]}
    monkeypatch.setattr(pr, "_fetch_pexels_image_urls",
                        lambda q, n=15: catalog.get(q, []))
    used = set()
    out1 = pr.resolve_pexels_tags('src="q1"', used=used)
    assert 'https://img/A.jpg' in out1
    # second file, same query, shared used-set -> must pick B, not A
    out2 = pr.resolve_pexels_tags('src="q1"', used=used)
    assert 'https://img/B.jpg' in out2


def test_falls_back_to_placeholder_when_no_results(monkeypatch):
    monkeypatch.setattr(pr, "_fetch_pexels_image_urls", lambda q, n=15: [])
    out = pr.resolve_pexels_tags('src="nothing matches"')
    assert "picsum.photos" in out


def test_identical_query_repeated_reuses_same_url(monkeypatch):
    # The SAME query twice should resolve to the same URL (it's one map entry).
    catalog = {"same q": ["https://img/A.jpg", "https://img/B.jpg"]}
    monkeypatch.setattr(pr, "_fetch_pexels_image_urls",
                        lambda q, n=15: catalog.get(q, []))
    out = pr.resolve_pexels_tags('src="same q"\nsrc="same q"')
    assert out.count('https://img/A.jpg') == 2
