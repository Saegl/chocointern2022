from uuid import UUID, uuid4

import aioredis
import tortoise
import ujson
from sanic import Sanic, response
from sanic.request import Request
from tortoise.contrib.sanic import register_tortoise
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from mini_showcase import providers, validation, models, settings, tasks
from mini_showcase.error_handlers import (
    BookingNotFound,
    OfferNotFound,
    SearchRequestNotFound,
    configure_error_handlers,
)


app = Sanic("mini-showcase")

register_tortoise(
    app,
    db_url=settings.DB_URI,
    modules={"models": ["mini_showcase.models"]},
    generate_schemas=True,
)
configure_error_handlers(app)


@app.listener("before_server_start")
async def init_before(app, loop):  # pragma: no cover
    app.ctx.redis = aioredis.from_url(
        settings.REDIS_URL, decode_responses=True
    )

    # Load currency on start
    await tasks.update_currency(app)

    # Then update currency every day at 12:00 by Almaty time
    scheduler = AsyncIOScheduler({"event_loop": loop})
    scheduler.configure(timezone=timezone("Asia/Almaty"))
    scheduler.add_job(tasks.update_currency, "cron", hour=12, args=[app])
    scheduler.start()


@app.listener("after_server_stop")
async def cleanup(app, _):  # pragma: no cover
    await app.ctx.redis.close()


@app.post("/search")
@validation.validate(validation.SearchRequest)
async def create_search(request: Request):
    # Generate new UUID
    search_id = str(uuid4())

    await app.ctx.redis.setex(
        search_id,
        settings.REDIS_SEARCH_TTL,
        ujson.dumps({"status": "PENDING", "items": []}),
    )

    # Start searching without blocking
    app.add_task(tasks.load_search_and_save(app, search_id, request.json))
    return response.json({"id": search_id})


@app.get("/search/<search_id:uuid>")
async def get_search_by_id(_, search_id: UUID):
    redis: aioredis.Redis = app.ctx.redis
    search_id = str(search_id)

    search_data = await redis.get(search_id)
    if not search_data:
        raise SearchRequestNotFound()

    data = ujson.loads(search_data)
    return response.json(
        {
            "search_id": search_id,
            "status": data["status"],
            "items": data["items"],
        }
    )


@app.get("/offers/<offer_id:uuid>")
async def get_offer_by_id(_, offer_id: UUID):
    redis: aioredis.Redis = app.ctx.redis

    data = await redis.get(f"offer:{offer_id}")
    if not data:
        raise OfferNotFound()
    return response.raw(data, content_type="application/json")


@app.get("/booking")
async def get_booking(request: Request):
    email = request.args.get("email")
    phone = request.args.get("phone")
    page = request.args.get("page", None)
    limit = request.args.get("limit", None)

    filter_params = {}
    if email:
        filter_params["email"] = email
    if phone:
        filter_params["phone"] = phone

    offers_query = models.Booking.filter(**filter_params)
    total = await offers_query.count()
    if page:
        offers_query = offers_query.offset(int(page) * int(limit)).limit(
            int(limit)
        )

    offers = await offers_query

    items = [
        (await models.BookingPydantic.from_tortoise_orm(offer)).dict()
        for offer in offers
    ]

    return response.json(
        {
            "page": page,
            "limit": limit,
            "total": total,
            "items": items,
        },
        default=str,
    )


@app.post("/booking")
@validation.validate(validation.BookingRequest)
async def create_booking(request: Request):
    await validation.check_document_expiration(app.ctx.redis, request.json)
    provider_response = await providers.book_offer(request.json)
    await models.Booking.create(**provider_response)
    return response.json(provider_response)


@app.get("/booking/<booking_id:uuid>")
async def get_booking_by_id(_, booking_id: UUID):
    try:
        booking = await models.Booking.get(id=booking_id)
    except tortoise.exceptions.DoesNotExist:
        raise BookingNotFound()
    booking_pydantic = await models.BookingPydantic.from_tortoise_orm(booking)
    return response.raw(
        booking_pydantic.json(), content_type="application/json"
    )


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=8000)
