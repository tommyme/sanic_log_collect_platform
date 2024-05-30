from app import app
import sanic
from sanic.response import text as TEXT, json as JSON

@app.get("/get")    # query
async def some_get(request: sanic.Request):
    return TEXT('get')

@app.post('/post')  # body json query
async def some_post(request: sanic.Request):
    return TEXT('post')
