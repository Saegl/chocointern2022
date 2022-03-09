import os


def load_file(filepath):
    if not os.path.exists(filepath):
        return None

    with open(filepath, "r", encoding='utf8') as f:
        return f.read()


async def pseudo_async(val):
    return val
