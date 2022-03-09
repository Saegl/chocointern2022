import os
import sys

import ujson
from pytest import fixture
from sanic import Sanic

from utils import load_file


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir)
)
sys.path.insert(0, PROJECT_ROOT)


class RedisMock:
    def __init__(self):
        self.mem = {}

    def show_mem(self):
        print(self.mem)

    async def get(self, key):
        return self.mem.get(key)

    async def set(self, key, value):
        self.mem[key] = value

    async def setex(self, key, timeout, value):
        self.mem[key] = value


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
def app(redis):
    from mini_showcase import app as sanic_app

    sanic_app.app.ctx.redis = redis

    test_app = Sanic("test-app")
    test_app.router = sanic_app.app.router
    test_app.ctx.redis = redis

    return test_app
