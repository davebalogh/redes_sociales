# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, Label
from wtforms.validators import DataRequired
from project.models import NetworkModel
from flask import flash, session, redirect
from dateutil import parser
from datetime import datetime
import json
import oauth2
import os
import urllib

# https://wtforms.readthedocs.io/en/latest/index.html

# OAUTH
def oauth_req(url, key, secret, consumer_key, consumer_secret, http_method="GET", post_body=b"", http_headers=None):
    consumer = oauth2.Consumer(key=consumer_key, secret=consumer_secret)
    token = oauth2.Token(key=key, secret=secret)
    client = oauth2.Client(consumer, token)
    resp, content = client.request(url, method=http_method, body=post_body, headers=http_headers )
    #print(content)
    return content

def json_str(json_obj):
    return json.dumps(json_obj, indent=2, sort_keys=True)

def get_account_settings(access_token, access_token_secret, consumer_key, consumer_secret):
    home_timeline = oauth_req('https://api.twitter.com/1.1/account/settings.json', access_token, access_token_secret, consumer_key, consumer_secret)

    data = home_timeline.decode('utf-8', 'replace')
    obj = json.loads(data)

    print(json_str(obj))

# FORMS

class FormList(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class FormEdit(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

#TWITTER

@app.route('/twitter', methods=['GET'])
def twitterList():
    if 'user_id' in session:
        form = FormList(request.form)
        networkList = NetworkModel.Twitter.select()

        if session['is_admin'] != 1:
            networkList = NetworkModel.Twitter.select().where(NetworkModel.Twitter.user_id == session['user_id'])

        show_message_css = 'hide'
        show_message_text = ''
        show_message_type = 'success'
        if 'result' in request.args:
            show_message_css = ''
            if request.args['result'] == 'ok':
                show_message_text = 'La información se guardo correctamente'
            else:
                show_message_type = 'danger'
                show_message_text = 'Hubo un problema al realizar la acción'

        return render_template('twitter/index.html', form=form, networks=networkList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type)
    else:
        return redirect ('/logout')


@app.route('/twitter/edit/<int:id>/<int:network_id>', methods=['GET', 'POST'])
def twitterEdit(id=None, network_id=None):
    if 'user_id' in session:
        form = FormEdit(request.form)
        currentNet = NetworkModel.Twitter()

        if id != None and id != 0:
            currentNet = NetworkModel.Twitter.get(NetworkModel.Twitter.twitter_id == id)

        if request.method == 'GET':
            if currentNet.twitter_id == None:
                currentNet = None

            return render_template('twitter/edit.html', form=form, network=currentNet)
        elif request.method == 'POST':
            currentNet.user_id = session['user_id']
            currentNet.username = request.form['username']

            currentNet.consumer_key = request.form['consumer_key']
            currentNet.consumer_secret = request.form['consumer_secret']
            currentNet.access_token = request.form['access_token']
            currentNet.access_token_secret = request.form['access_token_secret']
            currentNet.network_id = network_id

            home_timeline = oauth_req('https://api.twitter.com/1.1/account/settings.json', currentNet.access_token, currentNet.access_token_secret, currentNet.consumer_key, currentNet.consumer_secret)
            data = home_timeline.decode('utf-8', 'replace')
            obj = json.loads(data)

            if 'errors' in obj:
                flash(obj['errors'][0]['message'], 'error')
                return render_template('twitter/edit.html', form=form, network=currentNet)

            
            if currentNet.username != obj['screen_name']:
                flash('Nombre de usuario diferente', 'error')
                return render_template('twitter/edit.html', form=form, network=currentNet)


            if id == None:
                user_profile = oauth_req('https://api.twitter.com/1.1/users/show.json?screen_name='+currentNet.username, currentNet.access_token, currentNet.access_token_secret, currentNet.consumer_key, currentNet.consumer_secret)
                data_profile = user_profile.decode('utf-8', 'replace')
                obj_profile = json.loads(data_profile)
                #print(json_str(obj_profile))
                
                newFriend = NetworkModel.Friend()
                newFriend.external_uuid = obj_profile['id_str']
                newFriend.name = str(obj_profile['name'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.username = str(obj_profile['screen_name'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.image_url = str(obj_profile['profile_image_url'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.network_id = network_id
                newFriend.is_visible = 0
                newFriend.save()

                owner_friend_id = NetworkModel.Friend.select().order_by(NetworkModel.Friend.friend_id.desc()).get().friend_id

                currentNet.friend_id = owner_friend_id

            currentNet.save()

            if id == None:
                last_twitter_id = NetworkModel.Twitter.select().order_by(NetworkModel.Twitter.twitter_id.desc()).get().twitter_id
                currentNetwork = NetworkModel.Network.get(NetworkModel.Network.network_id == network_id)
                currentNetwork.twitter_id = last_twitter_id
                currentNetwork.save()

                

            return redirect ('/twitter?result=ok')
            #return render_template('twitter/edit.html', form=form, network=currentNet)

    else:
        return redirect ('/logout')


@app.route('/twitter/new/<int:network_id>', methods=['GET', 'POST'])
def twitterNew(network_id):
    return twitterEdit(None, network_id)


@app.route('/twitter/delete/<int:id>', methods=['GET', 'POST'])
def twitterDelete(id):
    if 'user_id' in session:
        if id != None:
            currentNet = NetworkModel.Twitter.get(NetworkModel.Twitter.twitter_id == id)
            parentNet = NetworkModel.Network.get(NetworkModel.Network.twitter_id == id)
            networkList = NetworkModel.Tweet.delete().where(NetworkModel.Tweet.twitter_id == id)
            if currentNet.twitter_id != None:
                networkList.execute()
                currentNet.delete_instance()
                parentNet.delete_instance()
                return redirect ('/twitter?result=ok')
        return redirect ('/twitter?result=fail')
    else:
        return redirect ('/logout')


#TWEETS

@app.route('/twitter/tweet/<int:twitter_id>', methods=['GET', 'POST'])
def twitterTweet(twitter_id):
    if 'user_id' in session:
        currentNet = NetworkModel.Twitter.get(NetworkModel.Twitter.twitter_id == twitter_id)
        form = FormEdit(request.form)

        if request.method == 'GET':
            return render_template('twitter/tweet.html', form=form, network=currentNet)
        else:
            currentTweet = NetworkModel.Tweet()
            currentTweet.user_id = session['user_id']
            currentTweet.twitter_id = twitter_id
            currentTweet.text = request.form['tweet']
            # URLENCODEAR EL TWEET
            params = urllib.parse.urlencode({ 'status': currentTweet.text })

            home_timeline = oauth_req('https://api.twitter.com/1.1/statuses/update.json?' + params, currentNet.access_token, currentNet.access_token_secret, currentNet.consumer_key, currentNet.consumer_secret, http_method='POST')

            data = home_timeline.decode('utf-8', 'replace')
            obj = json.loads(data)
            currentTweet.tweet_uuid = str(obj['id'])
            currentTweet.save()

            return redirect ('/twitter/tweets/' + str(twitter_id) + '?result=ok')
    else:
        return redirect ('/logout')



@app.route('/twitter/tweets/<int:twitter_id>', methods=['GET'])
def tweetList(twitter_id):
    if 'user_id' in session:
        form = FormList(request.form)
        currentNet = NetworkModel.Twitter.get(NetworkModel.Twitter.twitter_id == twitter_id)

        #import new tweets
        home_timeline = oauth_req('https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=' + currentNet.username, currentNet.access_token, currentNet.access_token_secret, currentNet.consumer_key, currentNet.consumer_secret)

        data = home_timeline.decode('utf-8', 'replace')
        obj = json.loads(data)
        #print(obj.encode('ascii', 'ignore'))

        for tweet in obj:
            selectTweet = NetworkModel.Tweet.select().where(NetworkModel.Tweet.tweet_uuid == tweet['id_str'])

            if selectTweet.count() == 0:
                newTweet = NetworkModel.Tweet()
                newTweet.user_id = session['user_id']
                newTweet.twitter_id = twitter_id
                newTweet.text = str(tweet['text'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newTweet.tweet_uuid = tweet['id_str']

                newTweet.date = parser.parse(tweet['created_at'])
                newTweet.save()

        
        networkList = NetworkModel.Tweet.select().where(NetworkModel.Tweet.twitter_id == twitter_id).order_by(NetworkModel.Tweet.date.desc())
        
        if session['is_admin'] == 1:
            networkList = NetworkModel.Tweet.select().where(NetworkModel.Tweet.twitter_id == twitter_id).order_by(NetworkModel.Tweet.date.desc())

        show_message_css = 'hide'
        show_message_text = ''
        show_message_type = 'success'
        if 'result' in request.args:
            show_message_css = ''
            if request.args['result'] == 'ok':
                show_message_text = 'La información se guardo correctamente'
            else:
                show_message_type = 'danger'
                show_message_text = 'Hubo un problema al realizar la acción'

        return render_template('twitter/tweets.html', form=form, twitter=currentNet, networks=networkList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type)
    else:
        return redirect ('/logout')


@app.route('/twitter/tweet/delete/<int:tweet_id>', methods=['GET', 'POST'])
def tweetDelete(tweet_id):
    if 'user_id' in session:
        if id != None:
            
            currenTweet = NetworkModel.Tweet.get(NetworkModel.Tweet.tweet_id == tweet_id)
            if currenTweet.tweet_id != None:
                currentNet = NetworkModel.Twitter.get(NetworkModel.Twitter.twitter_id == currenTweet.twitter_id)
                oauth_req('https://api.twitter.com/1.1/statuses/destroy/' + currenTweet.tweet_uuid + '.json', currentNet.access_token, currentNet.access_token_secret, currentNet.consumer_key, currentNet.consumer_secret, http_method='POST')
                #home_timeline = 
                #data = home_timeline.decode('utf-8', 'replace')

                currenTweet.delete_instance()
                return redirect ('/twitter/tweets/' + str(currentNet.twitter_id) + '?result=ok')
            else:
                return redirect ('/twitter?result=fail')
    else:
        return redirect ('/logout')


# friends
@app.route('/twitter/friends/<int:twitter_id>', methods=['GET'])
def twitterFriends(twitter_id):
    if 'user_id' in session:
        form = FormList(request.form)
        currentNet = NetworkModel.Twitter.get(NetworkModel.Twitter.twitter_id == twitter_id)

        #import new tweets
        home_timeline = oauth_req('https://api.twitter.com/1.1/friends/list.json?count=50', currentNet.access_token, currentNet.access_token_secret, currentNet.consumer_key, currentNet.consumer_secret)
      
        data = home_timeline.decode('utf-8', 'replace')
        obj = json.loads(data)


        for friend in obj['users']:
            #print(str(friend['name'].encode('ascii', 'ignore').decode('utf-8', 'replace')))
            selectFriend= NetworkModel.Friend.select().where(NetworkModel.Friend.external_uuid == friend['id_str'], NetworkModel.Friend.network_id == currentNet.network_id)

            if selectFriend.count() == 0:
                newFriend = NetworkModel.Friend()
                newFriend.external_uuid = friend['id_str']
                newFriend.name = str(friend['name'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.username = str(friend['screen_name'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.image_url = str(friend['profile_image_url'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.network_id = currentNet.network_id
                newFriend.save()

        friendList = NetworkModel.Friend.select().where(NetworkModel.Friend.network_id == currentNet.network_id, NetworkModel.Friend.is_visible == 1)
        

        show_message_css = 'hide'
        show_message_text = ''
        show_message_type = 'success'
        if 'result' in request.args:
            show_message_css = ''
            if request.args['result'] == 'ok':
                show_message_text = 'El mensaje se envió correctamente'
            else:
                show_message_type = 'danger'
                show_message_text = 'Hubo un problema al realizar la acción'

        return render_template('twitter/friends.html', form=form, twitter=currentNet, networks=friendList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type)
    else:
        return redirect ('/logout')

#Messages
@app.route('/twitter/<int:network_id>/friend/message/<int:friend_id>', methods=['GET', 'POST'])
def twitterMessage(network_id, friend_id):
    if 'user_id' in session:
        currentFriend = NetworkModel.Friend.get(NetworkModel.Friend.network_id == network_id and NetworkModel.Friend.friend_id == friend_id )
        currentNet = NetworkModel.Twitter.get(NetworkModel.Twitter.network_id == network_id)

        form = FormEdit(request.form)

        if request.method == 'GET':
            return render_template('twitter/message.html', form=form, friend=currentFriend)
        else:
            params = '''{"event": 
                {"type": "message_create", "message_create": 
                    {"target": 
                        {"recipient_id": "''' + currentFriend.external_uuid  +  '''"}, 
                        "message_data": {"text": "''' + request.form['message'] + '''"}}}}'''

            params = str(params).encode('utf-8')

            dm = oauth_req('https://api.twitter.com/1.1/direct_messages/events/new.json', currentNet.access_token, currentNet.access_token_secret, currentNet.consumer_key, currentNet.consumer_secret, http_method='POST', post_body=params, http_headers={"Content-Type": "application/json"})

            #print(json_str(json.loads(dm.decode('utf-8', 'replace'))))

            return redirect ('/twitter/friends/' + str(currentNet.twitter_id) +'?result=ok')

    else:
        return redirect ('/logout')


@app.route('/twitter/inbox/<int:network_id>', methods=['GET'])
def messageList(network_id):
    if 'user_id' in session:
        form = FormList(request.form)
        currentNet = NetworkModel.Twitter.get(NetworkModel.Twitter.network_id == network_id)

        #import new tweets
        home_timeline = oauth_req('https://api.twitter.com/1.1/direct_messages/events/list.json', currentNet.access_token, currentNet.access_token_secret, currentNet.consumer_key, currentNet.consumer_secret)
        #print(home_timeline)
        data = home_timeline.decode('utf-8', 'replace')
        obj = json.loads(data)
        #print(json_str(obj))

        for event in obj['events']:
            
            selectMessage = NetworkModel.Message.select().where(NetworkModel.Message.external_uuid == event['id'], NetworkModel.Message.network_id == currentNet.network_id)
            if selectMessage.count() == 0 and currentNet.friend_id.external_uuid != event['message_create']['sender_id']:
                senderFriend = NetworkModel.Friend.select().where(NetworkModel.Friend.external_uuid == event['message_create']['sender_id'], NetworkModel.Friend.network_id == network_id)
                if senderFriend.count() == 0:
                    newFriend = NetworkModel.Friend()
                    newFriend.external_uuid = event['message_create']['sender_id']
                    newFriend.name = 'Desconocido'
                    newFriend.username = 'desconocido'
                    newFriend.network_id = network_id
                    newFriend.is_visible = 0
                    newFriend.save()

                    senderFriend = NetworkModel.Friend.select().where(NetworkModel.Friend.external_uuid == event['message_create']['sender_id'], NetworkModel.Friend.network_id == network_id)

          
                newMessage = NetworkModel.Message()
                newMessage.text = str(event['message_create']['message_data']['text'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newMessage.external_uuid = event['id']
                newMessage.network_id = network_id
                newMessage.friend_sender_id = senderFriend[0].friend_id
                #newMessage.created_timestamp = datetime.utcfromtimestamp(int(event['created_timestamp'])) 

                newMessage.save()

        messageList = NetworkModel.Message.select().where(NetworkModel.Message.network_id == currentNet.network_id).order_by(NetworkModel.Message.message_id.desc())

        show_message_css = 'hide'
        show_message_text = ''
        show_message_type = 'success'
        if 'result' in request.args:
            show_message_css = ''
            if request.args['result'] == 'ok':
                show_message_text = 'La información se guardo correctamente'
            else:
                show_message_type = 'danger'
                show_message_text = 'Hubo un problema al realizar la acción'

        return render_template('twitter/inbox.html', form=form, twitter=currentNet, networks=messageList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type)
    else:
        return redirect ('/logout')