import traceback

from sanic import response
from sanic.exceptions import NotFound
from pydantic import ValidationError


class OfferNotFound(NotFound):
    message = "Offer not found"


class SearchRequestNotFound(NotFound):
    message = "Search request not found"


class BookingNotFound(NotFound):
    message = "Booking not found"


async def validation_handler(_, error: ValidationError):
    details = []
    for e in error.errors():
        for field in e["loc"]:
            details.append({"msg": e["msg"], "field": field})

    return response.json({"detail": details}, 422)


async def not_found_handler(_, error: NotFound):
    return response.json({"detail": [error.message]}, error.status_code)


async def server_error_handler(_, error: Exception):
    traceback.print_tb(error.__traceback__)
    status_code = error.status_code if hasattr(error, "status_code") else 500
    return response.json({"error": str(error)}, status_code)


def configure_error_handlers(app):
    app.error_handler.add(ValidationError, validation_handler)
    app.error_handler.add(NotFound, not_found_handler)
    app.error_handler.add(Exception, server_error_handler)
