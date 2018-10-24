import peewee
from peewee import *
from project.models import BaseModel, Login


# http://docs.peewee-orm.com/en/latest/peewee/models.html
class Network(BaseModel.Base):
    network_id = peewee.IntegerField(primary_key=True)
    name = peewee.CharField()
    is_active = peewee.IntegerField()
    owner_id = peewee.ForeignKeyField(Login.User, backref='Networks')
    network_type = peewee.CharField()
    created_date = peewee.DateTimeField()