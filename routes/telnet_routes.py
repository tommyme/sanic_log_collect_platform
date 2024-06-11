from app import app
from sanic.response import text as TEXT, json as JSON
from tortoise import run_async
from db_handle import db_init
import json
import telnetlib3
from telnetlib3 import TelnetReader, TelnetWriter
import asyncio
import sanic
import time
from utils.index import query_build, query_build_trust
from models.scriptModel import ScriptRecords, ScriptRecordsFields
# run_async(db_init())


class telnetManager:
    websocket: any
    reader: TelnetReader
    writer: TelnetWriter
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def init_telnet(self):
        self.reader, self.writer = await telnetlib3.open_connection(self.host, self.port)
        print(id(self.reader), id(self.writer))
    def close(self):
        self.reader.close()
        self.writer.close()
    async def read_from_telnet(self):
        try:
            while line := await anext(self.reader):
                if self.reader.connection_closed or self.writer.connection_closed:
                    # 尝试重新连接 telnet
                    self.close()
                    await self.init_telnet()
                    continue
                await self.websocket.send(line)
        except Exception as e:
            await self.websocket.send(f"Error reading from Telnet: {str(e)}")

    async def read_from_websocket(self):
        try:
            async for message in self.websocket:
                data = json.loads(message)
                if 'command' in data:
                    if self.writer.connection_closed:
                        self.close()
                        await self.init_telnet()
                    self.writer.write(data['command'])
                    await self.writer.drain()
                    if data['command'].startswith('xxxx'):
                        self.close()
        except Exception as e:
            print(f"Error reading from WebSocket: {str(e)}")

    async def handle_telnet(self, websocket):
        self.websocket = websocket

        try:
            await self.init_telnet()
            
            # Create tasks to read from Telnet and WebSocket
            telnet_task = asyncio.create_task(self.read_from_telnet())
            websocket_task = asyncio.create_task(self.read_from_websocket())
            
            # Wait for both tasks to complete
            await asyncio.gather(telnet_task, websocket_task)
        except Exception as e:
            await websocket.send(f"Error: {str(e)}")
        finally:
            self.reader.close()
            # await reader.wait_closed()

@app.websocket('/telnet')
async def telnet(request, ws):
    message = await ws.recv()
    data = json.loads(message)
    address = data.get('address')
    port = data.get('port')

    if address and port:
        manager = telnetManager(address, int(port))
        await manager.handle_telnet(ws)
    else:
        await ws.send("Invalid address or port")


@app.post('/script/update')
async def script_update(request: sanic.Request):
    pass

@app.post('/script/add')
async def script_add(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, ScriptRecordsFields.create_needed_fields)
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    await ScriptRecords.create(**query)
    return JSON({"res": "succ"})

@app.post('/script/query')
async def script_query(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, ['name'])
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    res = await ScriptRecords.filter(**query).values()
    return JSON(res)

@app.post('/script/all')
async def script_all(request: sanic.Request):
    res = await ScriptRecords.all().values()
    return JSON(res)

@app.post('/script/del')
async def script_del(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, ['name'])
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    await ScriptRecords.delete(**query)
    return JSON({"res": "succ"})