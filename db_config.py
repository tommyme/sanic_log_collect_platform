DB_CONFIG = {
    "connections": {
        "mainAppConn": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": "db.sqlite3"},
        },
    },
    "apps": {
        "mainApp": {"models": ["models.logModel", "models.scriptModel", "aerich.models"], "default_connection": "mainAppConn"},
        # "events": {"models": ["__main__"], "default_connection": "second"},
    },
}