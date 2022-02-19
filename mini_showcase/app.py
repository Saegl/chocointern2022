from uuid import UUID, uuid4
from pydantic import ValidationError

import aioredis
import ujson
from sanic import Sanic, response
from sanic.request import Request
from tortoise.contrib.sanic import register_tortoise

from mini_showcase import providers
from mini_showcase import validation
from mini_showcase import models
from mini_showcase import settings


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


@app.listener("after_server_stop")
async def cleanup(app, loop):
    await app.ctx.redis.close()


async def load_search_and_save(search_id, request_data):
    provider_response = await providers.offers_search(request_data)

    redis: aioredis.Redis = app.ctx.redis

    # Save provider_response for "get_search_by_id" handler
    await redis.set(search_id, ujson.dumps(provider_response))

    # Save offers for "get_offer_by_id" handler
    for offer in provider_response["items"]:
        await redis.set(f'offer:{offer["id"]}', ujson.dumps(offer))


@app.post("/search")
async def create_search(request: Request):
    # Generate new UUID
    search_id = str(uuid4())
    try:
        validated_request = validation.SearchRequest(**request.json).dict()
    except ValidationError as e:
        # response.json() is not used,
        # because e.json() already serialized by pydantic
        return response.raw(body=e.json(), content_type="application/json")

    # Start searching without blocking
    app.add_task(load_search_and_save(search_id, validated_request))
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
async def create_booking(request: Request):
    # TODO validation
    provider_response = await providers.offers_booking(request.json)
    await models.Booking.create(**provider_response)
    return response.json(provider_response)


@app.get("/booking/<booking_id:uuid>")
async def get_booking_by_id(request: Request, booking_id: UUID):
    booking = await models.Booking.get(id=str(booking_id))
    booking_pydantic = await models.BookingPydantic.from_tortoise_orm(booking)
    return response.raw(
        booking_pydantic.json(), content_type="application/json"
    )


@app.get("/test")
async def test(request: Request):
    return response.json({"test": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
