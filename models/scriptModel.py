from tortoise import Tortoise, connections, fields, run_async
from tortoise.exceptions import OperationalError
from tortoise.models import Model


class ScriptRecords(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(50, unique=True)
    content = fields.TextField()
    host = fields.CharField(30)
    port = fields.CharField(10)

    def __str__(self):
        return self.name

    class Meta:
        app = "mainApp"

import copy
class ScriptRecordsFields:
    create_needed_fields = copy.copy(ScriptRecords._meta.fields)
    create_needed_fields.remove("id")