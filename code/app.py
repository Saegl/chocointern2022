from uuid import UUID

from sanic import Sanic, response
from sanic.request import Request
import aioredis

from code.offers import OFFER_EXAMPLE
from code.booking import (
    BOOKING_ID_DETAILS_EXAMPLE,
    BOOKING_EXAMPLE,
    BOOKING_LIST_EXAMPLE,
)
from code import settings


app = Sanic("mini-showcase")


@app.listener("before_server_start")
async def init_before(app, loop):
    app.ctx.redis = aioredis.from_url(settings.REDIS_URL)


@app.listener("after_server_stop")
async def cleanup(app, loop):
    await app.ctx.redis.close()


@app.post("/search")
async def create_search(request: Request):
    return response.json({"id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da"})


@app.get("/search/<search_id:uuid>")
async def get_search_by_id(request: Request, search_id: UUID):
    status = "PENDING"  # PENDING or DONE
    return response.json(
        {"search_id": str(search_id), "status": status, "items": []}
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
