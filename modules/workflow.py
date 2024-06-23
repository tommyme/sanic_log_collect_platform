import asyncio
import paramiko
from paramiko import SSHClient
from models.scriptModel import SshCreditRecords, ProfileRecords
import subprocess
# example config
example_config = {
    "name": "some workflow step",
    "type": "sftp upload",
    "ssh": 1,
    "src": "/home/xxx.bin",
    "dst": "/home/ybw/xxx.bin"
}
async def run_step(config: dict):
    if config['type'] == 'local exec':
        return await handle_local_exec(config)
    elif config['type'] == 'sftp upload':
        return await handle_sftp_upload(config)
    elif config['type'] == 'ssh exec':
        return await handle_ssh_exec(config)
    elif config['type'] == 'sftp download':
        return await handle_sftp_download(config)
    else:
        raise Exception(f"Unknown step type: {config['type']}")

async def handle_sftp_upload(config: dict):
    id = config['ssh']
    src, dst = config['src'], config['dst']
    profile = await ProfileRecords.get(id=id)
    credit = await SshCreditRecords.get(profile=profile)
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(profile.host, profile.port, credit.name, credit.passwd)
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(src, dst)
        sftp_client.close()
        ssh_client.close()
        return {
            'status': 'success',
            'res': f"Uploaded {src} to {dst}"
        }
    except Exception as e:
        return {
            'status': 'error',
            'res': str(e)
        }

async def handle_sftp_download(config: dict):
    id = config['ssh']
    src, dst = config['src'], config['dst']
    profile = await ProfileRecords.get(id=id)
    credit = await SshCreditRecords.get(profile=profile)
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(profile.host, profile.port, credit.name, credit.passwd)
        sftp_client = ssh_client.open_sftp()
        sftp_client.get(src, dst)
        sftp_client.close()
        ssh_client.close()
        return {
            'status': 'success',
            'res': f"Downloaded {src} to {dst}"
        }
    except Exception as e:
        return {
            'status': 'error',
            'res': str(e)
        }

async def handle_local_exec(config: dict):
    cmd = config['cmd']
    process = subprocess.Popen(['pwsh.exe', '-Command', cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    status = 'error'
    if process.returncode == 0:
        status = 'success'
    return {
        'status': status,
        'res': stdout.decode('utf-8'),
    }

async def handle_ssh_exec(config: dict):
    id = config['ssh']
    cmd = config['cmd']
    profile = await ProfileRecords.get(id=id)
    credit = await SshCreditRecords.get(profile=profile)
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(profile.host, profile.port, credit.name, credit.passwd)
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        output = stdout.read().decode('utf-8') + stderr.read().decode('utf-8')
        return {
            'status': 'success',
            'res': output
        }
    except Exception as e:
        return {
            'status': 'error',
            'res': str(e)
        }





