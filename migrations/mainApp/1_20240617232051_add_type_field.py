from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "profilerecords" ADD "type" VARCHAR(10) NOT NULL  DEFAULT 'telnet';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "profilerecords" DROP COLUMN "type";"""
