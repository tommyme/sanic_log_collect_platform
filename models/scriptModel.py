from tortoise import Tortoise, connections, fields, run_async
from tortoise.exceptions import OperationalError
from tortoise.models import Model
import copy


class ProfileRecords(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(50, unique=True)
    host = fields.CharField(30)
    port = fields.CharField(10)
    type = fields.CharField(10, default='telnet')

    def __str__(self):
        return self.name

    class Meta:
        app = "mainApp"

class ScriptsRecords(Model):
    sid = fields.IntField(pk=True)
    sname = fields.CharField(50, unique=True)
    content = fields.TextField()
    profile = fields.ForeignKeyField('mainApp.ProfileRecords', related_name='scripts')

    def __str__(self):
        return self.sname
    
    class Meta:
        app = "mainApp"

class SshCreditRecords(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    passwd = fields.TextField()
    profile = fields.ForeignKeyField('mainApp.ProfileRecords', related_name='ssh')

    def __str__(self):
        return self.name
    
    class Meta:
        app = "mainApp"

class WorkflowRecords(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    workflow = fields.TextField()

    def __str__(self):
        return self.name
    
    class Meta:
        app = "mainApp"

class WorkflowRecordsFields:
    fields = WorkflowRecords._meta.fields
    create_needed_fields = copy.copy(WorkflowRecords._meta.fields)
    create_needed_fields.remove("id")

class SshCreditRecordsFields:
    create_needed_fields = copy.copy(SshCreditRecords._meta.fields)
    create_needed_fields.remove("id")


class ScriptsFields:
    create_needed_fields = copy.copy(ScriptsRecords._meta.fields)
    create_needed_fields.remove("sid")

class ProfileRecordsFields:
    fields = ProfileRecords._meta.fields
    create_needed_fields = copy.copy(ProfileRecords._meta.fields)
    create_needed_fields.remove("id")