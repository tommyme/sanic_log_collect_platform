from app import app
import sanic
from sanic.response import text as TEXT, json as JSON
from models.logModel import LogRecords
import copy
from tortoise import run_async
from db_handle import db_init
run_async(db_init())

@app.get("/get")    # query
async def some_get(request: sanic.Request):
    return TEXT('get')

@app.post('/addLog')  # body json query
async def some_post(request: sanic.Request):
    json_data: dict = request.json
    needed_fields = copy.copy(LogRecords._meta.fields)
    needed_fields.remove("id")
    lake_keys = [key for key in needed_fields if key not in json_data.keys()]
    if lake_keys:
        return JSON({"lake of keys": lake_keys})
    data_item = {k: str(v) for k, v in json_data.items() if k in needed_fields}
    await LogRecords.create(**data_item)
    return JSON({"res": "succ"})

@app.get("/logs")
async def show_logs(request: sanic.Request):
    log_items = await LogRecords.all()
    for i in log_items:
        print(i.chip, i.version, i.exectime, i.case, i.logger, i.level)
    return TEXT("ok")
    

@app.websocket('/websocket')
async def do_websocket(request: sanic.Request, ws: sanic.Websocket):
    async for msg in ws:
        await ws.send(msg)