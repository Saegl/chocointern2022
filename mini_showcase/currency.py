import xml.etree.ElementTree as ET
from datetime import date

import httpx


CURRENCY_URL_FORMAT = (
    "https://www.nationalbank.kz/rss/get_rates.cfm?fdate={day}.{month}.{year}"
)


async def async_get(url):
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    return res.content


async def load_currency() -> dict[str, float]:
    now = date.today()
    url = CURRENCY_URL_FORMAT.format(
        day=now.day, month=now.month, year=now.year
    )
    res = await async_get(url)
    root = ET.fromstring(res)

    currencies = {"KZT": 1.0}
    for child in filter(lambda e: e.tag == "item", root):
        currency_name = None
        currency_value = None
        for prop in child:
            if prop.tag == "title":
                currency_name = prop.text
            if prop.tag == "description":
                currency_value = float(prop.text)
        if not currency_name or not currency_value:
            raise ValueError("Wrong XML currency format")
        currencies[currency_name] = currency_value
    return currencies


def convert_to_kzt(
    currencies: dict[str, float], from_currency_type: str, amount: float
):
    return amount * currencies[from_currency_type]


def convert_from_kzt(
    currencies: dict[str, float], to_currency_type: str, amount: float
):
    return amount / currencies[to_currency_type]


def convert_items_currency(items, to_currency, currencies):
    for item in items:
        currency_type = item["price"]["currency"]
        amount = item["price"]["amount"]

        if currency_type == to_currency:
            continue

        in_kzt = convert_to_kzt(currencies, currency_type, amount)

        item["price"]["amount"] = convert_from_kzt(
            currencies, to_currency, in_kzt
        )
        item["price"]["currency"] = to_currency
