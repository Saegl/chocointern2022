import httpx

from mini_showcase import settings
from mini_showcase.error_handlers import OfferNotFound


AVIA_API_ROOT = "https://avia-api.k8s-test.aviata.team"

OFFERS_SEARCH = AVIA_API_ROOT + "/offers/search"
OFFERS_BOOKING = AVIA_API_ROOT + "/offers/booking"
PROVIDERS = ["Amadeus", "Sabre"]


async def search_offers(json_data, provider_name) -> list[dict]:
    json_data['provider'] = provider_name
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                OFFERS_SEARCH,
                json=json_data,
                timeout=settings.PROVIDERS_API_TIMEOUT,
            )
        response_json = res.json()
        return response_json['items']
    except httpx.TimeoutException:
        return []


async def book_offer(json_data) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            OFFERS_BOOKING,
            json=json_data,
            timeout=settings.PROVIDERS_API_TIMEOUT,
        )
    if res.status_code == 404:
        raise OfferNotFound()
    return res.json()
