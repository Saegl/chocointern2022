import os
import sys
from contextlib import asynccontextmanager

import ujson
from pytest import fixture
from sanic import Sanic

from utils import load_file


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir)
)
sys.path.insert(0, PROJECT_ROOT)


class RedisPipeMock:
    def __init__(self, redis):
        self.redis = redis

    def setex(self, key, ttl, value):
        self.redis.setex(key, ttl, value)

    async def execute(self):
        return []


class RedisMock:
    def __init__(self):
        self.mem = {}

    async def get(self, key):
        return self.mem.get(key)

    async def set(self, key, value):
        self.mem[key] = value

    async def setex(self, key, timeout, value):
        self.mem[key] = value

    @asynccontextmanager
    async def pipeline(self, *args, **kwargs):
        yield RedisPipeMock(self)


@fixture
def redis(mocker):
    return mocker.Mock(wraps=RedisMock())


@fixture
def book_example():
    return ujson.loads(load_file("tests/data/book_example.json"))


@fixture
def search_example():
    return ujson.loads(load_file("tests/data/search_example.json"))


@fixture
def offer_example():
    return ujson.loads(load_file("tests/data/offer_example.json"))


@fixture
def fake_currency():
    return ujson.loads(load_file("tests/data/fake_currency.json"))


@fixture
def app(redis, fake_currency):
    from mini_showcase import app as sanic_app

    sanic_app.app.ctx.redis = redis
    sanic_app.app.ctx.currency = fake_currency

    test_app = Sanic("test-app")
    test_app.router = sanic_app.app.router
    test_app.ctx.redis = redis
    test_app.ctx.currency = fake_currency

    return test_app
