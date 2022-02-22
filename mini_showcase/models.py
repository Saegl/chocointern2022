from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Booking(Model):
    id = fields.UUIDField(pk=True)
    pnr = fields.CharField(max_length=256)
    expires_at = fields.CharField(max_length=256)
    phone = fields.CharField(max_length=256)
    email = fields.CharField(max_length=256)
    offer = fields.JSONField()
    passengers = fields.JSONField()


BookingPydantic = pydantic_model_creator(Booking)
