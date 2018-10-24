import peewee
from peewee import *

# http://docs.peewee-orm.com/en/latest/
# Connect to a MySQL database on network.
mysql_db = peewee.MySQLDatabase('redes_sociales', user='root', passwd='',
                         host='localhost', port=3306)


class Base(peewee.Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = mysql_db