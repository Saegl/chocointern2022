from sanic import response
from pydantic import ValidationError
from tortoise.exceptions import DoesNotExist


class OfferNotFound(Exception):
    pass


class SearchRequestNotFound(Exception):
    pass


class BookingNotFound(Exception):
    pass


async def validation_handler(request, error: ValidationError):
    details = []
    for e in error.errors():
        for field in e["loc"]:
            details.append({"msg": e["msg"], "field": field})

    return response.json({"detail": details}, 422)


async def booking_not_exist_handler(request, error: BookingNotFound):
    return response.json({"detail": ["Booking not found"]}, 404)


async def offer_not_found_handler(request, error: OfferNotFound):
    return response.json({"detail": ["Offer not found"]}, 404)


async def search_request_not_found_handler(
    request, error: SearchRequestNotFound
):
    return response.json({"detail": ["Search request not found"]}, 404)


def configure_error_handlers(app):
    app.error_handler.add(ValidationError, validation_handler)
    app.error_handler.add(BookingNotFound, booking_not_exist_handler)
    app.error_handler.add(OfferNotFound, offer_not_found_handler)
    app.error_handler.add(
        SearchRequestNotFound, search_request_not_found_handler
    )
