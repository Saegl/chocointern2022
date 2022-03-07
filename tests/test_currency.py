from copy import deepcopy
from mini_showcase.currency import (
    load_currency,
    convert_to_kzt,
    convert_from_kzt,
    convert_items_currency,
)


async def test_load():
    currency = await load_currency()
    assert "KZT" in currency
    assert "USD" in currency
    assert "EUR" in currency


async def test_conversion():
    currency = await load_currency()
    in_kzt = convert_to_kzt(currency, "USD", 100)

    # Convert back
    out_usd = convert_from_kzt(currency, "USD", in_kzt)

    assert out_usd == 100


async def test_items_conv():
    currency = {"KZT": 1.0, "USD": 2.0}
    offers = [  # Offers example, only price included, others fields omitted
        {
            "price": {"amount": 184724, "currency": "KZT"},
        },
        {
            "price": {"amount": 47742, "currency": "KZT"},
        },
        {
            "price": {"amount": 47742, "currency": "KZT"},
        },
    ]
    original_offers = deepcopy(offers)  # convert_items_currency works in-place
    convert_items_currency(offers, "USD", currency)

    for item, orig in zip(offers, original_offers):
        assert item["price"]["currency"] == "USD"
        assert item["price"]["amount"] == orig["price"]["amount"] / 2
