import peewee
from peewee import *

# http://docs.peewee-orm.com/en/latest/
# Connect to a MySQL database on network.
mysql_db = peewee.MySQLDatabase('redes_sociales', user='root', passwd='',
                         host='localhost', port=3306)


class BaseModel(peewee.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = mysql_db

# http://docs.peewee-orm.com/en/latest/peewee/models.html
class User(BaseModel):
    user_id = peewee.IntegerField(primary_key=True)
    username = peewee.CharField()
    password = peewee.CharField()
    is_active = peewee.SmallIntegerField()

mysql_db.connect()

query = User.select()

# To iterate:
for user in query:
    print(user.username)