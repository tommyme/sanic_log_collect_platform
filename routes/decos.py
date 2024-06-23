import sanic
import functools
from utils.index import query_build
from sanic.response import json as JSON

def validate_lake_keys(fields):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request: sanic.Request, *args):
            # 使用args是为了使用validate_lake_keys多次装饰时能够兼容
            json_data = request.json
            laked_keys, query = query_build(json_data, fields)
            if laked_keys:
                return JSON({"error": f"missing keys: {laked_keys}"}, 400)
            return await func(request, query)
        return wrapper
    return decorator