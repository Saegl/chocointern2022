from datetime import date, datetime
from inspect import isawaitable
from uuid import UUID
from typing import Literal
from functools import wraps

import ujson
import pydantic
from aioredis import Redis
from pydantic import (
    BaseModel,
    constr,
    conint,
    root_validator,
    validator,
    EmailStr,
)

from mini_showcase.error_handlers import OfferNotFound


class SearchRequest(BaseModel):
    cabin: Literal["Economy", "Business"] = "Economy"
    origin: constr(strict=True, min_length=3, max_length=3)
    destination: constr(strict=True, min_length=3, max_length=3)
    dep_at: str
    arr_at: str
    adults: conint(strict=True, ge=1, le=9) = 1
    children: conint(strict=True, ge=0, le=9) = 0
    infants: conint(strict=True, ge=0, le=9) = 0
    currency: constr(strict=True, min_length=3, max_length=3)

    @root_validator
    def maximum_number_of_people(cls, values):
        assert (
            values["adults"] + values["children"] + values["infants"] <= 9
        ), "Too many people, maximum is 9"
        return values

    @root_validator
    def more_adults_than_non_adults(cls, values):
        assert (
            values["adults"] >= values["children"] + values["infants"]
        ), "More non-adults than adults"
        return values

    @validator("dep_at", "arr_at")
    def dates_not_in_the_past(cls, val):
        assert date.fromisoformat(val) >= date.today(), "Dates in the past"
        return val


class PassengerDocument(BaseModel):
    number: str
    expires_at: str
    iin: constr(min_length=12, max_length=12)


class Passenger(BaseModel):
    gender: Literal["M", "F"]
    type: Literal["ADT", "CHD", "INF"]
    first_name: str
    last_name: str
    date_of_birth: str
    citizenship: constr(min_length=2, max_length=3)
    document: PassengerDocument

    @root_validator
    def check_age_type(cls, values):
        dob = date.fromisoformat(values["date_of_birth"])
        today = date.today()

        age = (
            today.year
            - dob.year
            - ((today.month, today.day) < (dob.month, dob.day))
        )
        age_type = values["type"]
        if age >= 16:
            right_age_type = "ADT"
        elif age >= 2:
            right_age_type = "CHD"
        else:
            right_age_type = "INF"
        assert (
            age_type == right_age_type
        ), f"type is {age_type} but should be {right_age_type}"
        return values


class BookingRequest(BaseModel):
    offer_id: UUID
    phone: constr(regex=r"[+](\d)*")  # noqa: F722
    email: EmailStr
    passengers: list[Passenger]


def validate(model):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            model(**request.json)
            response = f(request, *args, **kwargs)
            if isawaitable(response):
                response = await response
            return response

        return decorated_function

    return decorator


def extract_offer_arrival_dates(offer):
    for flight in offer["flights"]:
        for segment in flight["segments"]:
            flight_expiration = datetime.fromisoformat(
                segment["arr"]["at"]
            ).date()
            yield flight_expiration


async def check_document_expiration(redis: Redis, json_data: dict) -> bool:
    """
    Passenger document expiration
    must be greater by 6 months than offer arrival date
    raises pydantic.ValidationError if any document is expired
    """
    offer_id = json_data["offer_id"]
    offer_data = await redis.get(f"offer:{offer_id}")
    if not offer_data:
        raise OfferNotFound()
    offer = ujson.loads(offer_data)

    for flight_expiration in extract_offer_arrival_dates(offer):
        for passenger in json_data["passengers"]:
            doc = passenger["document"]
            doc_expiration = date.fromisoformat(doc["expires_at"])

            month_diff = (
                (doc_expiration.year - flight_expiration.year) * 12
                + doc_expiration.month
                - flight_expiration.month
                - (doc_expiration.day < flight_expiration.day)
            )

            if month_diff < 6:
                raise pydantic.ValidationError(
                    [
                        pydantic.error_wrappers.ErrorWrapper(
                            ValueError(
                                "Difference between passenger documents "
                                "expiration time and offer arrival date "
                                "must greater than 6 months"
                            ),
                            loc="expires_at",
                        )
                    ],
                    BookingRequest,
                )
    return False
