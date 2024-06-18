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
from models.scriptModel import ProfileRecords, ProfileRecordsFields, ScriptsFields, ScriptsRecords, SshCreditRecords, SshCreditRecordsFields
from tortoise.contrib.pydantic import pydantic_model_creator
import paramiko
from paramiko import SSHClient
from paramiko.client import AutoAddPolicy
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

class sshManager:
    def __init__(self, ssh_client):
        self.ssh_client = ssh_client
        self.channel = None
        self.websocket = None

    def init_ssh(self):
        self.channel = self.ssh_client.invoke_shell()
        self.channel.settimeout(0.0)

    def close(self):
        if self.channel:
            self.channel.close()
        self.ssh_client.close()

    async def read_from_ssh(self):
        try:
            while True:
                await asyncio.sleep(0.1)
                if self.channel.recv_ready():
                    output = self.channel.recv(1024).decode('utf-8')
                    await self.websocket.send(output)
        except Exception as e:
            await self.websocket.send(f"Error reading from SSH: {str(e)}")

    async def read_from_websocket(self):
        try:
            async for message in self.websocket:
                data = json.loads(message)
                if 'command' in data:
                    self.channel.send(data['command'])
        except Exception as e:
            await self.websocket.send(f"Error reading from WebSocket: {str(e)}")

    async def handle_ssh(self, websocket):
        self.websocket = websocket

        try:
            self.init_ssh()
            
            # Create tasks to read from SSH and WebSocket
            ssh_task = asyncio.create_task(self.read_from_ssh())
            websocket_task = asyncio.create_task(self.read_from_websocket())
            
            # Wait for both tasks to complete
            await asyncio.gather(ssh_task, websocket_task)
        except Exception as e:
            await websocket.send(f"Error: {str(e)}")
        finally:
            self.close()

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

@app.post('/profile/update')
async def profile_update(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, ProfileRecordsFields.create_needed_fields)
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    profiles = await ProfileRecords.filter(id=json_data['id'])
    if len(profiles) == 0:  # create new
        profile = ProfileRecords(**query)
        await profile.save()
    else:                   # update exists
        profile = profiles[0]
        profile.update_from_dict(query)
        await profile.save()
    return JSON({"res": "succ"})



@app.post('/script/update')
async def script_update(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, _ = query_build(json_data, ['profile'])
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    profile = await ProfileRecords.get(id=json_data['profile'])
    # 暂时不考虑改名的情况
    lake_keys, query = query_build(json_data, ScriptsFields.create_needed_fields)
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    scripts = await profile.scripts.filter(sid=json_data['sid'])
    # 考虑新建script的情况
    if len(scripts) == 0:
        profile = await ProfileRecords.get(id=json_data['profile'])
        query.update({'profile': profile})
        await ScriptsRecords(**query).save()
    else:
        # 通过sid筛选出来的结果唯一
        script = scripts[0]
        query.pop('profile')
        script.update_from_dict(query)
        await script.save()
    return JSON({'res': "succ"})

@app.post('/script/add')
async def script_add(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, ScriptsFields.create_needed_fields)
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    await ScriptsRecords.create(**query)
    return JSON({"res": "succ"})

@app.post('/script/query')
async def script_query(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, ['name'])
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    res = await ProfileRecords.filter(**query).values()
    return JSON(res)

@app.post('/script/allProfiles')
async def profile_all(request: sanic.Request):
    res = await ProfileRecords.all().values()
    return JSON(res)

@app.post("/script/allScripts")
async def script_all(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, ['name'])
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    profile = await ProfileRecords.get(**query)
    res = await ScriptsRecords.filter(profile=profile.id).values()
    print(res)
    return JSON(res)

@app.post('/script/del')
async def script_del(request: sanic.Request):
    json_data: dict = request.json
    lake_keys, query = query_build(json_data, ['name'])
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    await ProfileRecords.delete(**query)
    return JSON({"res": "succ"})

@app.websocket('/ssh')
async def ssh_conn(request: sanic.Request, ws):
    message = await ws.recv()
    json_data = json.loads(message)
    # 定义 SSH 和 SFTP 连接的参数
    hostname = json_data['host']
    port     = json_data['port']
    username = json_data['name']
    password = json_data['passwd']

    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    try:
        ssh_client.connect(hostname=hostname, port=port, username=username, password=password)
        manager = sshManager(ssh_client)
        await manager.handle_ssh(ws)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        ssh_client.close()

@app.post('/ssh/credits')
async def ssh_credit(request: sanic.Request):
    json_data = request.json
    lake_keys, query = query_build(json_data, ['name'])
    if lake_keys:
        return JSON({"lake of keys": lake_keys}, 400)
    profile = await ProfileRecords.get(**query)
    res = await SshCreditRecords.filter(profile=profile.id).values()
    return JSON(res)