from tortoise.contrib.sanic import register_tortoise
from tortoise import Tortoise, connections, fields, run_async
from tortoise.exceptions import OperationalError
from tortoise.models import Model

async def db_init():
    await Tortoise.init(
        {
            "connections": {
                "mainAppConn": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {"file_path": "db.sqlite3"},
                },
            },
            "apps": {
                "mainApp": {"models": ["models.logModel", "models.scriptModel"], "default_connection": "mainAppConn"},
                # "events": {"models": ["__main__"], "default_connection": "second"},
            },
        }
    )
    await Tortoise.generate_schemas()
