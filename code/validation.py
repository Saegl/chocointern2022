import datetime
from typing import Literal
from pydantic import BaseModel, constr, conint


class SearchRequest(BaseModel):
    provider: Literal["Amadeus", "Sabre"]
    cabin: Literal["Economy", "Business"] = "Economy"
    origin: constr(strict=True, min_length=3, max_length=3)
    destination: constr(strict=True, min_length=3, max_length=3)
    # TODO strict datetime validation
    # dep_at: datetime.datetime
    # arr_at: datetime.datetime
    dep_at: str
    arr_at: str
    # TODO adults + children + infants <= 9
    adults: conint(strict=True, ge=1, le=9) = 1
    children: conint(strict=True, ge=0, le=9) = 0
    infants: conint(strict=True, ge=0, le=9) = 0

    currency: constr(strict=True, min_length=3, max_length=3)


if __name__ == "__main__":
    example = {
        "provider": "Amadeus",
        "cabin": "Economy",
        "origin": "ALA",
        "destination": "NQZ",
        "dep_at": "2022-03-09",
        "arr_at": "2022-03-15",
        "adults": 1,
        "children": 0,
        "infants": 0,
        "currency": "KZT",
    }

    model = SearchRequest(**example)
    print(model)
    print(model.json())
