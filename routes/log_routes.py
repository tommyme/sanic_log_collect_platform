from app import app
import sanic
from sanic.response import text as TEXT, json as JSON
from models.logModel import LogRecords, LogRecordsFields
import copy
from tortoise import run_async
from db_handle import db_init
import json
import time
from utils.index import query_build, query_build_trust
run_async(db_init())


@app.get("/get")    # query
async def some_get(request: sanic.Request):
    return TEXT('get')

@app.post('/addLog')  # body json query
async def some_post(request: sanic.Request):
    st = time.time()
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, LogRecordsFields.create_needed_fields)
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    await LogRecords.create(**query)
    ed = time.time()
    print(ed - st)
    return JSON({"res": "succ"})

@app.get("/logs")
async def show_logs(request: sanic.Request):
    log_items = await LogRecords.all()
    for i in log_items:
        print(i.chip, i.version, i.exectime, i.case, i.logger, i.level)
    return TEXT("ok")

def check(keys):
    if keys == set(): 
        return ['chip']
    elif keys == {'chip'}:
        return ['version']
    elif keys == {'chip', 'version'}:
        return ['exectime', 'case']
    elif keys == {'chip', 'version', 'exectime'}:
        return ['case']
    elif keys == {'chip', 'version', 'case'}:
        return ['exectime']
    elif keys == {'chip', 'version', 'exectime', 'case'}:
        return ['iter']
    elif keys == {'chip', 'version', 'exectime', 'case', 'iter'}:
        return ['logger']
    elif keys == {'chip', 'version', 'exectime', 'case', 'iter', 'logger'}:
        return ['level']
    elif keys == {'chip', 'version', 'exectime', 'case', 'iter', 'logger', 'level'}:
        return []
    else:
        return None


@app.post("/sel")
async def get_sel(request: sanic.Request):
    json_data = request.json
    keys = set(json_data.keys())
    if retKeys:=check(keys):
        res = []
        for k in retKeys:
            qry_res = await LogRecords.filter(**json_data).distinct().values(k)
            qry_res = [{"value":i, "label": i[k]} for i in qry_res]
            res += qry_res
        return JSON(res)
    elif retKeys is None:
        return JSON({'res': 'err'}, 400)
    elif retKeys == []:
        return JSON([])
    else:
        return JSON({'res': 'err'}, 400)


from dataclasses import dataclass

@dataclass
class CtrlOpts:
    len: int
    offset: int

def get_ctrl_opt(src: dict):
    res = {}
    keys = list(src.keys())
    for k in keys:
        if k.startswith("__"):
            res[k[2:]] = src.pop(k)
    opt = CtrlOpts(**res)
    return opt

@app.websocket('/websocket')
async def do_websocket(request: sanic.Request, ws: sanic.Websocket):
    async for msg in ws:
        req = json.loads(msg)
        # req有__len __offset这两个field用于控制
        ctrl_opt = get_ctrl_opt(req)
        # 这里使用trust可以让前端发送请求的时候携带一些query的高级参数 目前还没有用到这个特性
        lake_keys, query = query_build_trust(req, LogRecordsFields.query_needed_fields)
        if lake_keys:
            raise Exception("lake of keys")
        res = await LogRecords.filter(**query).offset(ctrl_opt.offset).limit(ctrl_opt.len).values_list("content", flat=True)
        await ws.send(json.dumps(res))