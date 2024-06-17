from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "logrecords" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "chip" VARCHAR(10) NOT NULL,
    "version" VARCHAR(10) NOT NULL,
    "exectime" VARCHAR(30) NOT NULL,
    "case" VARCHAR(100) NOT NULL,
    "iter" INT NOT NULL,
    "logger" TEXT NOT NULL,
    "level" VARCHAR(10) NOT NULL,
    "content" TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS "profilerecords" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "host" VARCHAR(30) NOT NULL,
    "port" VARCHAR(10) NOT NULL
);
CREATE TABLE IF NOT EXISTS "scriptsrecords" (
    "sid" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "sname" VARCHAR(50) NOT NULL UNIQUE,
    "content" TEXT NOT NULL,
    "profile_id" INT NOT NULL REFERENCES "profilerecords" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
