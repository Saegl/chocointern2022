import asyncio
import xml.etree.ElementTree as ET
from datetime import date

import httpx


CURRENCY_URL_FORMAT = (
    "https://www.nationalbank.kz/rss/get_rates.cfm?fdate={day}.{month}.{year}"
)


async def load_currency() -> dict[str, float]:
    now = date.today()
    url = CURRENCY_URL_FORMAT.format(
        day=now.day, month=now.month, year=now.year
    )
    async with httpx.AsyncClient() as client:
        res = await client.get(url)
    root = ET.fromstring(res.content)

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


if __name__ == "__main__":
    # Check current currency
    # Run: `python -m mini_showcase.currency`
    from pprint import pprint

    data = asyncio.run(load_currency())
    pprint(data)
