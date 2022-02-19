import ujson
from aioredis import Redis

from mini_showcase import providers, settings


async def load_search_and_save(redis: Redis, search_id, request_data):
    provider_response = await providers.offers_search(request_data)

    # Save provider_response for "app.get_search_by_id" handler
    await redis.setex(
        search_id, settings.REDIS_SEARCH_TTL, ujson.dumps(provider_response)
    )

    # Save offers for "app.get_offer_by_id" handler
    async with redis.pipeline(transaction=True) as pipe:
        for offer in provider_response["items"]:
            pipe.setex(
                f'offer:{offer["id"]}',
                settings.REDIS_SEARCH_TTL,
                ujson.dumps(offer),
            )

        commands_success = await pipe.execute()
        assert all(commands_success)
