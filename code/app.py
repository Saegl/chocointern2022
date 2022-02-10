from uuid import UUID

from sanic import Sanic, response
from sanic.request import Request

from code.offers import OFFER_EXAMPLE
from code.booking import (
    BOOKING_ID_DETAILS_EXAMPLE,
    BOOKING_EXAMPLE,
    BOOKING_LIST_EXAMPLE,
)


app = Sanic("mini-showcase")


@app.post("/search")
async def search(request: Request):
    return response.json({"id": "d9e0cf5a-6bb8-4dae-8411-6caddcfd52da"})


@app.route("/search/<search_id:uuid>")
async def search(request: Request, search_id: UUID):
    status = "PENDING"  # PENDING or DONE
    return response.json(
        {"search_id": search_id, "status": status, "items": []}
    )


@app.route("/offers/<offer_id:uuid>")
async def offers(request: Request, offer_id: UUID):
    return response.json(OFFER_EXAMPLE)


@app.route("/booking")
async def booking(request: Request):
    return response.json(BOOKING_LIST_EXAMPLE)


@app.post("/booking")
async def booking(request: Request):
    return response.json(BOOKING_EXAMPLE)


@app.route("/booking/<booking_id:uuid>")
async def booking(request: Request, booking_id: UUID):
    return response.json(BOOKING_ID_DETAILS_EXAMPLE)


@app.route("/test")
async def test(request: Request):
    return response.json({"test": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
