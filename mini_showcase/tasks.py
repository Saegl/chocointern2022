import ujson
from aioredis import Redis

from mini_showcase import providers


async def load_search_and_save(redis: Redis, search_id, request_data):
    provider_response = await providers.offers_search(request_data)

    # Save provider_response for "get_search_by_id" handler
    await redis.set(search_id, ujson.dumps(provider_response))

    # Save offers for "get_offer_by_id" handler
    for offer in provider_response["items"]:
        await redis.set(f'offer:{offer["id"]}', ujson.dumps(offer))
