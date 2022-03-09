from datetime import date, datetime

import pytest
import pydantic
import ujson

from utils import load_file
from mini_showcase.validation import (
    BookingRequest,
    SearchRequest,
    check_document_expiration,
)
from mini_showcase.error_handlers import OfferNotFound


@pytest.fixture
def book_example():
    return ujson.loads(load_file("tests/data/book_example.json"))


@pytest.fixture
def search_example():
    return ujson.loads(load_file("tests/data/search_example.json"))


@pytest.fixture
def offer_example():
    return ujson.loads(load_file("tests/data/offer_example.json"))


def test_book_request(book_example):
    model = BookingRequest(**book_example)

    # Passenger age is more than 20 y.o.
    assert model.passengers[0].type == "ADT"  # He is adult

    # Passenger was born today
    # He is clearly not an adult
    date_of_birth = date.today()
    book_example["passengers"][0]["date_of_birth"] = date_of_birth.isoformat()

    with pytest.raises(pydantic.ValidationError):
        # type is ADT but should be INF (infant)
        BookingRequest(**book_example)


def test_search_request(search_example):
    s = SearchRequest(**search_example)
    assert s.cabin == "Economy"
    assert s.adults == 1
    assert s.children == 0


async def test_document_expiration(mocker, book_example, offer_example):
    async def make_async(val):
        return val

    # Check with valid documents
    redis = mocker.Mock()
    redis.get = mocker.Mock(
        return_value=make_async(ujson.dumps(offer_example))
    )

    await check_document_expiration(redis, book_example)

    # Check with expired documents
    # Passenger document expiration is equal to offer arrival date
    book_example["passengers"][0]["document"][
        "expires_at"
    ] = date.today().isoformat()
    offer_example["flights"][0]["segments"][0]["arr"][
        "at"
    ] = datetime.now().isoformat()

    redis.get = mocker.Mock(
        return_value=make_async(ujson.dumps(offer_example))
    )

    with pytest.raises(pydantic.ValidationError):
        await check_document_expiration(redis, book_example)

    # Offer not found
    redis.get = mocker.Mock(return_value=make_async(None))
    with pytest.raises(OfferNotFound):
        await check_document_expiration(redis, book_example)
