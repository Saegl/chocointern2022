from uuid import UUID, uuid4

from sanic import Sanic, response
from sanic.request import Request
import aioredis
import ujson

from code.offers import OFFER_EXAMPLE
from code.booking import (
    BOOKING_ID_DETAILS_EXAMPLE,
    BOOKING_EXAMPLE,
    BOOKING_LIST_EXAMPLE,
)
from code import settings
from code import providers


app = Sanic("mini-showcase")


@app.listener("before_server_start")
async def init_before(app, loop):
    app.ctx.redis = aioredis.from_url(
        settings.REDIS_URL, decode_responses=True
    )


@app.listener("after_server_stop")
async def cleanup(app, loop):
    await app.ctx.redis.close()


async def load_search_and_save(search_id, request_data):
    provider_response = await providers.search_api(request_data)

    redis: aioredis.Redis = app.ctx.redis
    await redis.set(search_id, ujson.dumps(provider_response))


@app.post("/search")
async def create_search(request: Request):
    # Generate new UUID
    search_id = str(uuid4())

    # Start searching without blocking
    app.add_task(load_search_and_save(search_id, request.json))
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
    return response.json(OFFER_EXAMPLE)


@app.get("/booking")
async def get_booking(request: Request):
    return response.json(BOOKING_LIST_EXAMPLE)


@app.post("/booking")
async def create_booking(request: Request):
    return response.json(BOOKING_EXAMPLE)


@app.get("/booking/<booking_id:uuid>")
async def get_booking_by_id(request: Request, booking_id: UUID):
    return response.json(BOOKING_ID_DETAILS_EXAMPLE)


@app.get("/test")
async def test(request: Request):
    return response.json({"test": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
