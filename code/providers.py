import asyncio
import httpx

from code import settings


AVIA_API_ROOT = "https://avia-api.k8s-test.aviata.team"

OFFERS_SEARCH = AVIA_API_ROOT + "/offers/search"


async def search_api(json_data):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            OFFERS_SEARCH,
            json=json_data,
            timeout=settings.PROVIDERS_API_TIMEOUT,
        )
    return res.json()


if __name__ == "__main__":
    from pprint import pprint

    ans = asyncio.run(
        search_api(
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
