from uuid import uuid4
import ujson
from mini_showcase.tasks import load_search_and_save


async def test_load_search_and_save_task(app, search_example, mocker):
    search_id = str(uuid4())

    # Create task with status PENDING
    await app.ctx.redis.set(
        search_id,
        ujson.dumps({"status": "PENDING", "items": []}),
    )

    # Start searching and save results in redis
    mocker.patch(
        "mini_showcase.providers.PROVIDERS", ['Amadeus']
    )  # search only in Amadeus
    await load_search_and_save(
        app,
        search_id,
        search_example,
    )

    # Check that task status is now DONE
    search_data = await app.ctx.redis.get(search_id)
    search_result = ujson.loads(search_data)
    assert search_result["status"] == "DONE"
