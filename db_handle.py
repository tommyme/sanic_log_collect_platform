from tortoise import Tortoise
from db_config import DB_CONFIG
async def db_init():
    await Tortoise.init(DB_CONFIG)
    await Tortoise.generate_schemas()
