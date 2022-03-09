import ujson
import asyncio
from aioredis import Redis

from mini_showcase import providers, settings, models
from mini_showcase.currency import convert_items_currency


async def load_provider(app, request_data, provider_name, search_id):
    redis: Redis = app.ctx.redis
    new_items = await providers.search_offers(request_data, provider_name)
    convert_items_currency(
        new_items, request_data["currency"], app.ctx.currency
    )

    old_data = ujson.loads(await redis.get(search_id))
    old_items = old_data["items"]

    # Update items for "app.get_search_by_id" handler
    await redis.setex(
        search_id,
        settings.REDIS_SEARCH_TTL,
        ujson.dumps({"status": "PENDING", "items": old_items + new_items}),
    )

    # Save offers for "app.get_offer_by_id" handler
    async with redis.pipeline(transaction=True) as pipe:
        for offer in new_items:
            pipe.setex(
                f'offer:{offer["id"]}',
                settings.REDIS_SEARCH_TTL,
                ujson.dumps(offer),
            )

        commands_success = await pipe.execute()
        assert all(commands_success)


async def load_search_and_save(app, search_id, request_data):
    redis: Redis = app.ctx.redis
    await asyncio.gather(
        *[
            load_provider(app, request_data, provider_name, search_id)
            for provider_name in providers.PROVIDERS
        ]
    )

    # Update status to DONE
    items = ujson.loads(await redis.get(search_id))["items"]
    await redis.setex(
        search_id,
        settings.REDIS_SEARCH_TTL,
        ujson.dumps({"status": "DONE", "items": items}),
    )


async def update_currency(app):  # pragma: no cover (Currencies tested in test_currency.py)
    currency = await models.Currency.get_current_currency()
    app.ctx.currency = currency.snapshot
