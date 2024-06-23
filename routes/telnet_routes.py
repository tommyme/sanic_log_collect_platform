from app import app
from sanic.response import text as TEXT, json as JSON
import json
import telnetlib3
from telnetlib3 import TelnetReader, TelnetWriter
import asyncio
import sanic
import time
from modules.workflow import run_step
from routes.decos import validate_lake_keys
from models.scriptModel import ProfileRecords, ProfileRecordsFields, ScriptsFields, ScriptsRecords, SshCreditRecords, SshCreditRecordsFields, WorkflowRecords, WorkflowRecordsFields
import paramiko
from paramiko import SSHClient
from paramiko.client import AutoAddPolicy

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
@validate_lake_keys(ProfileRecordsFields.create_needed_fields)
async def profile_update(request: sanic.Request, query):
    # 这里用json_data的id; query里面没有id
    new_data = request.json.get('id') is None
    if new_data:
        profile = await ProfileRecords.create(**query)
    else:
        profile = await ProfileRecords.get(id=request.json['id'])
        profile.update_from_dict(query)
        await profile.save()
    return JSON({"res": "succ"})



@app.post('/script/update')
@validate_lake_keys(['profile'])
@validate_lake_keys(ScriptsFields.create_needed_fields)
async def script_update(request: sanic.Request, query):
    json_data: dict = request.json
    profile = await ProfileRecords.get(id=json_data['profile'])
    # 暂时不考虑改名的情况
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
@validate_lake_keys(ScriptsFields.create_needed_fields)
async def script_add(request: sanic.Request, query):
    await ScriptsRecords.create(**query)
    return JSON({"res": "succ"})

@app.post('/script/query')
@validate_lake_keys(['name'])
async def script_query(request: sanic.Request, query):
    res = await ProfileRecords.filter(**query).values()
    return JSON(res)

@app.post('/script/allProfiles')
async def profile_all(request: sanic.Request):
    res = await ProfileRecords.all().values()
    return JSON(res)

@app.post("/script/allScripts")
@validate_lake_keys(['name'])
async def script_all(request: sanic.Request, query):
    profile = await ProfileRecords.get(**query)
    res = await ScriptsRecords.filter(profile=profile.id).values()
    return JSON(res)

@app.post('/script/del')
@validate_lake_keys(ScriptsFields.create_needed_fields)
async def script_del(request: sanic.Request, query):
    await ScriptsRecords.delete(**query)
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
@validate_lake_keys(['name'])
async def ssh_credit(request: sanic.Request, query):
    profile = await ProfileRecords.get(**query)
    res = await SshCreditRecords.filter(profile=profile.id).values()
    return JSON(res)


@app.post("/workflow/all")
async def workflow_all(request: sanic.Request):
    origin = await WorkflowRecords.all().values()
    result = []
    for item in origin:
        item['workflow'] = json.loads(item['workflow'])
        result.append(item)
    return JSON(result)

@app.post("/workflow/save")
@validate_lake_keys(WorkflowRecordsFields.create_needed_fields)
async def workflow_save(request: sanic.Request, query):
    # 这里用json_data的id; query里面没有id
    new_data = request.json.get('id') is None
    if new_data:
        workflow = await WorkflowRecords.create(**query)
    else:
        workflow = await WorkflowRecords.get(id=request.json['id'])
        workflow.update_from_dict(query)
        await workflow.save()
    return JSON({"res": "succ"})


@app.post("/workflow/run")
async def workflow_run(request: sanic.Request):
    # 直接传对应的step进来run, res是对应step的res
    json_data = request.json
    res = await run_step(json_data)
    return JSON(res)

