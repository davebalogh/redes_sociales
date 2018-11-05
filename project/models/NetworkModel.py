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


class Twitter(BaseModel.Base):
    twitter_id = peewee.IntegerField(primary_key=True)
    username = peewee.CharField()
    consumer_key = peewee.CharField()
    consumer_secret = peewee.CharField()
    access_token = peewee.CharField()
    access_token_secret = peewee.CharField()
    network_id = peewee.ForeignKeyField(Network, backref='Twitters')
    user_id = peewee.ForeignKeyField(Login.User, backref='Twitters')

class Tweet(BaseModel.Base):
    tweet_id = peewee.IntegerField(primary_key=True)
    text = peewee.CharField()
    date = peewee.DateTimeField()
    twitter_id = peewee.ForeignKeyField(Twitter, backref='Tweets')
    user_id = peewee.ForeignKeyField(Login.User, backref='Tweets')
    tweet_uuid = peewee.CharField()