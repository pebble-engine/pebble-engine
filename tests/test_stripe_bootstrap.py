"""Tests for pebble/stripe_bootstrap.py — the one-shot CLI that creates
Pebble Starter + Pro products + prices in Stripe.

These tests stub the Stripe SDK entirely. They pin two things that
matter for a future SDK upgrade:

1. The metadata + recurring accessors handle stripe 15.x's StripeObject
   (which doesn't subclass dict, so ``.get`` raises AttributeError).
2. The bootstrap is idempotent — a re-run reuses existing products /
   prices found by metadata + amount, never duplicates.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from pebble import stripe_bootstrap


# ---- _stripe_metadata_get -------------------------------------------------

def test_metadata_get_returns_value_via_indexing():
    """Stripe SDK 15.x's StripeObject supports ``obj["key"]`` but not
    ``obj.get("key")``. The helper uses indexing + try/except — must
    return the value when present."""
    obj = SimpleNamespace(metadata={"pebble_plan": "starter"})
    assert stripe_bootstrap._stripe_metadata_get(obj, "pebble_plan") == "starter"


def test_metadata_get_returns_none_when_key_missing():
    obj = SimpleNamespace(metadata={"other_key": "x"})
    assert stripe_bootstrap._stripe_metadata_get(obj, "pebble_plan") is None


def test_metadata_get_returns_none_when_metadata_is_none():
    obj = SimpleNamespace(metadata=None)
    assert stripe_bootstrap._stripe_metadata_get(obj, "pebble_plan") is None


def test_metadata_get_returns_none_when_no_metadata_attribute():
    obj = SimpleNamespace()
    assert stripe_bootstrap._stripe_metadata_get(obj, "pebble_plan") is None


def test_metadata_get_handles_stripeobject_like_without_get():
    """Real failure mode that drove this helper: 15.x StripeObject raises
    AttributeError on ``.get`` because it overrides __getattr__ to look
    only inside the dict, missing dict's inherited method."""
    class StripeLike:
        def __init__(self, **kw):
            self._data = kw
        def __getitem__(self, key):
            return self._data[key]
        # NO .get method — that's the bug we worked around

    obj = SimpleNamespace(metadata=StripeLike(pebble_plan="pro"))
    assert stripe_bootstrap._stripe_metadata_get(obj, "pebble_plan") == "pro"


# ---- _stripe_recurring_interval ------------------------------------------

def test_recurring_interval_returns_month():
    price = SimpleNamespace(recurring={"interval": "month", "interval_count": 1})
    assert stripe_bootstrap._stripe_recurring_interval(price) == "month"


def test_recurring_interval_none_for_one_time_price():
    """One-time prices have recurring=None — the helper must not crash."""
    price = SimpleNamespace(recurring=None)
    assert stripe_bootstrap._stripe_recurring_interval(price) is None


# ---- bootstrap idempotency ------------------------------------------------

def _make_fake_stripe_with_no_products():
    fake = MagicMock()
    # Use side_effect (not return_value) so each call gets a fresh iterator —
    # bootstrap() calls Product.list once per plan, sharing a return_value
    # would exhaust the iterator on the first call.
    fake.Product.list.return_value.auto_paging_iter.side_effect = lambda: iter([])
    fake.Product.create.side_effect = lambda **kw: SimpleNamespace(
        id=f"prod_new_{kw['metadata']['pebble_plan']}",
        metadata=kw["metadata"],
    )
    fake.Price.list.return_value.auto_paging_iter.side_effect = lambda: iter([])
    fake.Price.create.side_effect = lambda **kw: SimpleNamespace(
        id=f"price_new_{kw['metadata']['pebble_plan']}",
        unit_amount=kw["unit_amount"],
        currency=kw["currency"],
        recurring=kw.get("recurring"),  # None for one-time prices
    )
    return fake


def test_bootstrap_creates_all_plans_when_account_empty():
    fake = _make_fake_stripe_with_no_products()
    result = stripe_bootstrap.bootstrap(fake)
    assert result["starter"]["product_id"] == "prod_new_starter"
    assert result["starter"]["price_id"]   == "price_new_starter"
    assert result["pro"]["product_id"]     == "prod_new_pro"
    assert result["pro"]["price_id"]       == "price_new_pro"
    assert result["setup_call"]["product_id"] == "prod_new_setup_call"
    assert result["setup_call"]["price_id"]   == "price_new_setup_call"
    # Three products created (starter, pro, setup_call)
    assert fake.Product.create.call_count == 3
    assert fake.Price.create.call_count == 3


def test_bootstrap_reuses_existing_products_on_rerun():
    """The big idempotency guarantee — running this in two sessions
    against the same Stripe account must NOT duplicate the catalog."""
    existing_starter = SimpleNamespace(
        id="prod_existing_starter",
        metadata={"pebble_plan": "starter"},
    )
    existing_pro = SimpleNamespace(
        id="prod_existing_pro",
        metadata={"pebble_plan": "pro"},
    )
    existing_setup_call = SimpleNamespace(
        id="prod_existing_setup_call",
        metadata={"pebble_plan": "setup_call"},
    )
    existing_starter_price = SimpleNamespace(
        id="price_existing_starter",
        unit_amount=2900,
        currency="usd",
        recurring={"interval": "month"},
    )
    existing_pro_price = SimpleNamespace(
        id="price_existing_pro",
        unit_amount=5900,
        currency="usd",
        recurring={"interval": "month"},
    )
    existing_setup_price = SimpleNamespace(
        id="price_existing_setup_call",
        unit_amount=9900,
        currency="usd",
        recurring=None,
    )

    all_products = [existing_starter, existing_pro, existing_setup_call]

    fake = MagicMock()
    # Fresh iterator on each call so multiple find_existing_product calls
    # each see all three products.
    fake.Product.list.return_value.auto_paging_iter.side_effect = lambda: iter(all_products)
    # Price.list returns the matching price for whatever product is asked
    def price_list(*, product, **_kw):
        m = MagicMock()
        if product == "prod_existing_starter":
            m.auto_paging_iter.return_value = iter([existing_starter_price])
        elif product == "prod_existing_pro":
            m.auto_paging_iter.return_value = iter([existing_pro_price])
        elif product == "prod_existing_setup_call":
            m.auto_paging_iter.return_value = iter([existing_setup_price])
        else:
            m.auto_paging_iter.return_value = iter([])
        return m
    fake.Price.list.side_effect = price_list

    result = stripe_bootstrap.bootstrap(fake)

    # Existing IDs reused — nothing new created
    assert result["starter"]    == {"product_id": "prod_existing_starter",
                                    "price_id": "price_existing_starter"}
    assert result["pro"]        == {"product_id": "prod_existing_pro",
                                    "price_id": "price_existing_pro"}
    assert result["setup_call"] == {"product_id": "prod_existing_setup_call",
                                    "price_id": "price_existing_setup_call"}
    fake.Product.create.assert_not_called()
    fake.Price.create.assert_not_called()


# ---- find_existing_one_time_price ----------------------------------------

def test_find_existing_one_time_price_returns_matching():
    """Finds a price with recurring=None and matching amount."""
    one_time = SimpleNamespace(unit_amount=9900, currency="usd", recurring=None)
    recurring = SimpleNamespace(unit_amount=9900, currency="usd",
                                recurring={"interval": "month"})

    fake = MagicMock()
    fake.Price.list.return_value.auto_paging_iter.return_value = iter([recurring, one_time])
    result = stripe_bootstrap.find_existing_one_time_price(fake, "prod_x", 9900)
    assert result is one_time


def test_find_existing_one_time_price_returns_none_when_only_recurring():
    """Does NOT return a monthly price even if the amount matches."""
    recurring = SimpleNamespace(unit_amount=9900, currency="usd",
                                recurring={"interval": "month"})
    fake = MagicMock()
    fake.Price.list.return_value.auto_paging_iter.return_value = iter([recurring])
    assert stripe_bootstrap.find_existing_one_time_price(fake, "prod_x", 9900) is None


# ---- ensure_setup_call creates one-time price ----------------------------

def test_ensure_setup_call_creates_price_without_recurring():
    """The Price.create call for a setup call must NOT include the
    `recurring` key — Stripe rejects one-time prices that have it."""
    fake = MagicMock()
    fake.Product.list.return_value.auto_paging_iter.return_value = iter([])
    fake.Product.create.return_value = SimpleNamespace(id="prod_sc", metadata={})
    fake.Price.list.return_value.auto_paging_iter.return_value = iter([])
    fake.Price.create.return_value = SimpleNamespace(id="price_sc")

    stripe_bootstrap.ensure_setup_call(fake, stripe_bootstrap.SETUP_CALLS[0])

    price_kwargs = fake.Price.create.call_args.kwargs
    assert "recurring" not in price_kwargs
    assert price_kwargs["unit_amount"] == 9900
    assert price_kwargs["currency"] == "usd"
