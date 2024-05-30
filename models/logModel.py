from tortoise import Tortoise, connections, fields, run_async
from tortoise.exceptions import OperationalError
from tortoise.models import Model


class LogRecords(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    def __str__(self):
        return self.name

    class Meta:
        app = "mainApp"