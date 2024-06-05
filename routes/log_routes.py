from app import app
import sanic
from sanic.response import text as TEXT, json as JSON
from models.logModel import LogRecords, LogRecordsFields
import copy
from tortoise import run_async
from db_handle import db_init
import json
run_async(db_init())

def get_lake_keys(data: dict, needed_fields):
    return [key for key in needed_fields if key not in data.keys()]

def build_keys_dict(data: dict, needed_fields):
    return {k: v for k, v in data.items() if k in needed_fields}

def query_build(data, needed_fields):
    lake_keys = get_lake_keys(data, needed_fields)
    query = build_keys_dict(data, needed_fields)
    return lake_keys, query


@app.get("/get")    # query
async def some_get(request: sanic.Request):
    return TEXT('get')

@app.post('/addLog')  # body json query
async def some_post(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, LogRecordsFields.create_needed_fields)
    if lake_keys:
        return JSON({"lake of keys": lake_keys})
    await LogRecords.create(**query)
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
        try:
            req = json.loads(msg)
            lake_keys, query = query_build(req, LogRecordsFields.query_needed_fields)
            if lake_keys:
                raise Exception("lake of keys")
            res = await LogRecords.filter(**query).values()
            ws.send(json.dumps(res))
        except:
            continue
        await ws.send(msg)