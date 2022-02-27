from uuid import UUID, uuid4

import aioredis
import ujson
from pydantic import ValidationError
from sanic import Sanic, json, response
from sanic.request import Request
from tortoise.contrib.sanic import register_tortoise
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from mini_showcase import providers, validation, models, settings, tasks


app = Sanic("mini-showcase")

register_tortoise(
    app,
    db_url=settings.DB_URI,
    modules={"models": ["mini_showcase.models"]},
    generate_schemas=True,
)


@app.listener("before_server_start")
async def init_before(app, loop):
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
async def cleanup(app, loop):
    await app.ctx.redis.close()


@app.post("/search")
@validation.validate(validation.SearchRequest)
async def create_search(request: Request):
    # Generate new UUID
    search_id = str(uuid4())
    # Start searching without blocking
    app.add_task(
        tasks.load_search_and_save(app.ctx.redis, search_id, request.json)
    )
    return response.json({"id": search_id})


@app.get("/search/<search_id:uuid>")
async def get_search_by_id(request: Request, search_id: UUID):
    redis: aioredis.Redis = app.ctx.redis
    search_id = str(search_id)

    if search_data := await redis.get(search_id):
        status = "DONE"
        data = ujson.loads(search_data)
        items = data["items"]
    else:
        status = "PENDING"
        items = []

    return response.json(
        {"search_id": search_id, "status": status, "items": items}
    )


@app.get("/offers/<offer_id:uuid>")
async def get_offer_by_id(request: Request, offer_id: UUID):
    redis: aioredis.Redis = app.ctx.redis

    data = await redis.get(f"offer:{offer_id}")
    return response.raw(data, content_type="application/json")


@app.get("/booking")
async def get_booking(request: Request):
    return response.json(request.query_args)


@app.post("/booking")
@validation.validate(validation.BookingRequest)
async def create_booking(request: Request):
    provider_response = await providers.book_offer(request.json)
    await models.Booking.create(**provider_response)
    return response.json(provider_response)


@app.get("/booking/<booking_id:uuid>")
async def get_booking_by_id(request: Request, booking_id: UUID):
    booking = await models.Booking.get(id=booking_id)
    booking_pydantic = await models.BookingPydantic.from_tortoise_orm(booking)
    return response.raw(
        booking_pydantic.json(), content_type="application/json"
    )


@app.get("/test")
async def test(request: Request):
    return response.json({"test": True})


async def server_validation_handler(request, error: ValidationError):
    details = []
    for e in error.errors():
        for field in e['loc']:
            details.append({
                'msg': e['msg'],
                'field': field
            })
    
    return response.json({
        "detail": details
    }, 422)


app.error_handler.add(ValidationError, server_validation_handler)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
