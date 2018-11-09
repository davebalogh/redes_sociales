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
    twitter_id = peewee.IntegerField()


class Friend(BaseModel.Base):
    friend_id = peewee.IntegerField(primary_key=True)
    name = peewee.CharField()
    username = peewee.CharField()
    external_uuid = peewee.CharField()
    image_url = peewee.CharField()
    network_id = peewee.ForeignKeyField(Network, backref='Friends')
    is_visible = peewee.IntegerField()

class Twitter(BaseModel.Base):
    twitter_id = peewee.IntegerField(primary_key=True)
    username = peewee.CharField()
    consumer_key = peewee.CharField()
    consumer_secret = peewee.CharField()
    access_token = peewee.CharField()
    access_token_secret = peewee.CharField()
    network_id = peewee.ForeignKeyField(Network, backref='Twitters')
    user_id = peewee.ForeignKeyField(Login.User, backref='Twitters')
    friend_id = peewee.ForeignKeyField(Friend, backref='Twitters')

class Tweet(BaseModel.Base):
    tweet_id = peewee.IntegerField(primary_key=True)
    text = peewee.CharField()
    date = peewee.DateTimeField()
    twitter_id = peewee.ForeignKeyField(Twitter, backref='Tweets')
    user_id = peewee.ForeignKeyField(Login.User, backref='Tweets')
    tweet_uuid = peewee.CharField()


class Message(BaseModel.Base):
    message_id = peewee.IntegerField(primary_key=True)
    text = peewee.CharField()
    external_uuid = peewee.CharField()
    network_id = peewee.ForeignKeyField(Network, backref='Messages')
    friend_sender_id = peewee.ForeignKeyField(Friend, backref='Messages')
    friend_recipient_id = peewee.ForeignKeyField(Friend, backref='Messages')
    created_timestamp = peewee.DateTimeField()
    

