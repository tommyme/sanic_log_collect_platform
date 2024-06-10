import telnetlib3
import asyncio
import time
from telnetlib3 import TelnetReader

async def shell(reader: TelnetReader, writer):
    while True:
        writer.write('> ')
        await writer.drain()
        line = await reader.read(256)
        print(line)
        if not line:
            print('over...')
            reader.close()
            writer.close()
            return
        writer.write(f'{line}')
        await writer.drain()

async def main():
    loop = asyncio.get_event_loop()
    server = await telnetlib3.create_server(port=6023, shell=shell)
    await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())