from tortoise import Tortoise, connections, fields, run_async
from tortoise.exceptions import OperationalError
from tortoise.models import Model


class LogRecords(Model):
    id = fields.IntField(pk=True)
    chip = fields.CharField(10)
    version = fields.CharField(10)
    exectime = fields.DateField()
    case = fields.CharField(100)
    iter = fields.IntField()
    logger = fields.TextField()
    level = fields.CharField(10)
    content = fields.TextField()

    def __str__(self):
        return self.chip

    class Meta:
        app = "mainApp"

import copy
class LogRecordsFields:
    create_needed_fields = copy.copy(LogRecords._meta.fields)
    create_needed_fields.remove("id")
    query_needed_fields = copy.copy(LogRecords._meta.fields)
    query_needed_fields.remove("id")
    query_needed_fields.remove("content")
    