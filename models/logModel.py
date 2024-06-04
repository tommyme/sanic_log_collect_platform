from tortoise import Tortoise, connections, fields, run_async
from tortoise.exceptions import OperationalError
from tortoise.models import Model


class LogRecords(Model):
    id = fields.IntField(pk=True)
    chip = fields.TextField()
    version = fields.TextField()
    exectime = fields.TextField()
    case = fields.TextField()
    iter = fields.TextField()
    logger = fields.TextField()
    level = fields.TextField()

    def __str__(self):
        return self.chip

    class Meta:
        app = "mainApp"