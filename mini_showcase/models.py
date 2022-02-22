import datetime
from tortoise import Model, fields
from tortoise.exceptions import DoesNotExist
from tortoise.contrib.pydantic import pydantic_model_creator

from mini_showcase.currency import load_currency


class Booking(Model):
    id = fields.UUIDField(pk=True)
    pnr = fields.CharField(max_length=256)
    expires_at = fields.CharField(max_length=256)
    phone = fields.CharField(max_length=256)
    email = fields.CharField(max_length=256)
    offer = fields.JSONField()
    passengers = fields.JSONField()


BookingPydantic = pydantic_model_creator(Booking)


class Currency(Model):
    date = fields.DateField()
    snapshot = fields.JSONField()

    @staticmethod
    async def get_current_currency() -> "Currency":
        today = datetime.date.today()
        try:
            return await Currency.get(date=today)
        except DoesNotExist:
            snapshot = await load_currency()
            return await Currency.create(date=today, snapshot=snapshot)
