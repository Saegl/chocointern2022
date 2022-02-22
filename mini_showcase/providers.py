import asyncio
import httpx

from mini_showcase import settings


AVIA_API_ROOT = "https://avia-api.k8s-test.aviata.team"

OFFERS_SEARCH = AVIA_API_ROOT + "/offers/search"
OFFERS_BOOKING = AVIA_API_ROOT + "/offers/booking"


async def search_offers(json_data) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            OFFERS_SEARCH,
            json=json_data,
            timeout=settings.PROVIDERS_API_TIMEOUT,
        )
    return res.json()


async def book_offer(json_data) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            OFFERS_BOOKING,
            json=json_data,
            timeout=settings.PROVIDERS_API_TIMEOUT,
        )
    if res.status_code != 200:
        # TODO processing for 404, 422 in stage-third
        raise ValueError("status code is not 200")
    return res.json()


if __name__ == "__main__":
    from pprint import pprint

    ans = asyncio.run(
        search_offers(
            {
                "provider": "Amadeus",
                "cabin": "Economy",
                "origin": "ALA",
                "destination": "NQZ",
                "dep_at": "2022-03-09",
                "arr_at": "2022-03-15",
                "adults": 1,
                "children": 0,
                "infants": 0,
            }
        )
    )

    pprint(ans)
