from datetime import date
from uuid import UUID
from typing import Literal
from pydantic import (
    BaseModel,
    constr,
    conint,
    root_validator,
    validator,
    EmailStr,
)


class SearchRequest(BaseModel):
    provider: Literal["Amadeus", "Sabre"]
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
        assert values["adults"] + values["children"] + values["infants"] <= 9
        return values

    @root_validator
    def more_adults_than_non_adults(cls, values):
        assert values["adults"] >= values["children"] + values["infants"]
        return values

    @validator("dep_at", "arr_at")
    def dates_not_in_the_past(cls, val):
        assert date.fromisoformat(val) >= date.today()
        return val


class PassengerDocument(BaseModel):
    number: str
    expires_at: str  # TODO validate expires_at
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
            assert age_type == "ADT"
        elif age >= 2:
            assert age_type == "CHD"
        else:
            assert age_type == "INF"
        return values


class BookingRequest(BaseModel):
    offer_id: UUID
    phone: constr(regex=r"[+](\d)*")
    email: EmailStr
    passengers: list[Passenger]


if __name__ == "__main__":
    book_example = {
        "offer_id": "d5a7a5b7-a4a3-49e7-9c69-b44d2cbe15cf",
        "phone": "+77777777777",
        "email": "user@example.com",
        "passengers": [
            {
                "gender": "M",
                "type": "ADT",
                "first_name": "Craig",
                "last_name": "Bensen",
                "date_of_birth": "2001-06-13",
                "citizenship": "US",
                "document": {
                    "number": "N2343545634",
                    "expires_at": "2025-08-24",
                    "iin": "123456789123",
                },
            }
        ],
    }

    model = BookingRequest(**book_example)
    # print(model)
    print(model.json())
