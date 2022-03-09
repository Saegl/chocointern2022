import uuid
import pydantic
import ujson
import tortoise

from utils import pseudo_async


async def test_create_search(app, search_example):
    _, response = await app.asgi_client.post(
        "/search",
        json=search_example,
    )

    assert response.status == 200
    assert pydantic.types.UUID4(response.json["id"])


async def test_get_offer_by_id(app, offer_example):
    new_uuid = uuid.uuid4()
    _, response = await app.asgi_client.get(f"/offers/{new_uuid}")

    assert response.status == 404

    await app.ctx.redis.set(f"offer:{new_uuid}", ujson.dumps(offer_example))
    _, response = await app.asgi_client.get(f"/offers/{new_uuid}")

    assert response.status == 200


async def test_get_search_by_id(app):
    new_uuid = uuid.uuid4()
    _, response = await app.asgi_client.get(f"/search/{new_uuid}")

    assert response.status == 404

    await app.ctx.redis.set(
        f"{new_uuid}",
        ujson.dumps(
            {
                "search_id": str(new_uuid),
                "status": "DONE",
                "items": [],
            }
        ),
    )
    _, response = await app.asgi_client.get(f"/search/{new_uuid}")

    assert response.status == 200


async def test_get_booking_by_id(app, mocker):
    new_uuid = uuid.uuid4()
    fake_model = mocker.Mock()
    fake_model.json = mocker.Mock(return_value={})

    mocker.patch(
        "mini_showcase.app.models.Booking.get", return_value=pseudo_async(None)
    )
    mocker.patch(
        "mini_showcase.app.models.BookingPydantic.from_tortoise_orm",
        return_value=fake_model,
    )
    _, response = await app.asgi_client.get(f"/booking/{new_uuid}")
    assert response.status == 200

    mocker.patch(
        "mini_showcase.app.models.Booking.get",
        side_effect=tortoise.exceptions.DoesNotExist,
    )
    _, response = await app.asgi_client.get(f"/booking/{new_uuid}")
    assert response.status == 404


async def test_get_booking(app, mocker):
    class FilterMock:
        def __await__(self):
            async def ret_empty_list():
                return []

            return ret_empty_list().__await__()

        async def count(self):
            return 0

        def offset(self, _):
            return self

        def limit(self, _):
            return self

    filter_mock = mocker.Mock(wraps=FilterMock())

    mocker.patch(
        "mini_showcase.app.models.Booking.filter",
        return_value=filter_mock,
    )

    _, response = await app.asgi_client.get(
        "/booking?email=example@example.com&phone=+777712345678&page=0&limit=10"
    )

    assert response.status == 200
