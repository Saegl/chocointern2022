import ujson
from aioredis import Redis

from mini_showcase import providers


async def load_search_and_save(redis: Redis, search_id, request_data):
    provider_response = await providers.offers_search(request_data)

    # Save provider_response for "app.get_search_by_id" handler
    await redis.set(search_id, ujson.dumps(provider_response))

    # Save offers for "app.get_offer_by_id" handler
    async with redis.pipeline(transaction=True) as pipe:
        for offer in provider_response["items"]:
            pipe.set(f'offer:{offer["id"]}', ujson.dumps(offer))

        commands_success = await pipe.execute()
        assert all(commands_success)
