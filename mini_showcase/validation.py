from datetime import date
from typing import Literal
from pydantic import BaseModel, constr, conint, root_validator, validator


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
