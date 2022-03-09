from uuid import uuid4
import pytest
from mini_showcase import providers
from mini_showcase.error_handlers import OfferNotFound


async def test_search_offers(search_example):
    await providers.search_offers(search_example, "Amadeus")

    with pytest.raises(ValueError):
        # Wrong provider name
        await providers.search_offers(search_example, "Alpha")


async def test_search_offers_timeout(search_example, mocker):
    mocker.patch("mini_showcase.settings.PROVIDERS_API_TIMEOUT", 0.0001)
    res = await providers.search_offers(search_example, "Amadeus")

    # search_offers should return empty list if timeout is exceeded
    assert res == []


async def test_book_offer():
    book_post = {
        "offer_id": str(uuid4()),
        "phone": "+77777777777",
        "email": "user@example.com",
        "passengers": [
            {
                "gender": "M",
                "type": "ADT",
                "first_name": "Craig",
                "last_name": "Bensen",
                "date_of_birth": "1985-08-24",
                "citizenship": "US",
                "document": {
                    "number": "N2343545634",
                    "expires_at": "2025-03-09",
                    "iin": "123456789123",
                },
            }
        ],
    }
    with pytest.raises(OfferNotFound):
        # Offer cannot be found for newly created offer_id
        await providers.book_offer(book_post)
