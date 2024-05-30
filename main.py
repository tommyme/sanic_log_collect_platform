from tortoise import run_async
from db_handle import db_init
from app import app
import routes.log_routes


if __name__ == '__main__':
    run_async(db_init())
    app.run(host='127.0.0.1', port=8000, debug=True)