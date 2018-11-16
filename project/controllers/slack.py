# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, Label
from wtforms.validators import DataRequired
from project.models import NetworkModel
from flask import flash, session, redirect
import requests, json


# https://wtforms.readthedocs.io/en/latest/index.html

class FormList(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class FormEdit(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

def json_str(json_obj):
    return json.dumps(json_obj, indent=2, sort_keys=True)

@app.route('/slack', methods=['GET'])
def slackList():
    if 'user_id' in session:
        form = FormList(request.form)
        networkList = NetworkModel.Slack.select()

        if session['is_admin'] != 1:
            networkList = NetworkModel.Slack.select().where(NetworkModel.Slack.user_id == session['user_id'])

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

        return render_template('slack/index.html', form=form, networks=networkList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type, url_domain = request.headers.get('Host'))
    else:
        return redirect ('/logout')

@app.route('/slack/edit/<int:slack_id>/<int:network_id>', methods=['GET', 'POST'])
def slackEdit(slack_id=None, network_id=None):
    if 'user_id' in session:
        form = FormEdit(request.form)
        currentNet = NetworkModel.Slack()

        if slack_id != None:
            currentNet = NetworkModel.Slack.get(NetworkModel.Slack.slack_id == slack_id)

        if request.method == 'GET':
            if currentNet.slack_id == None:
                currentNet = None

            return render_template('slack/edit.html', form=form, network=currentNet)

        elif request.method == 'POST':

            url = "https://slack.com/api/auth.test"

            headers = {
                'cache-control': "no-cache",
                'authorization': "Bearer " + request.form['oauth_access_token']
                }

            response = requests.request("GET", url, headers=headers)
            resp = json.loads(response.text)

            if resp['ok'] == False:
                flash('Token inválido', 'error')
                return render_template('slack/edit.html', form=form, network=currentNet)

            urlTemp = 'https://' + request.form['workspace'] + '.slack.com/'
            if resp['url'] != urlTemp:
                flash('Workspace inválido', 'error')
                return render_template('slack/edit.html', form=form, network=currentNet)


            if slack_id == None:
                url_user = "https://slack.com/api/users.info?user=" + resp['user_id']

                headers_user = {
                    'cache-control': "no-cache",
                    'authorization': "Bearer " + request.form['oauth_access_token']
                    }

                response_user = requests.request("GET", url_user, headers=headers_user)
                resp_user = json.loads(response_user.text)
                
                newFriend = NetworkModel.Friend()
                newFriend.external_uuid = resp_user['user']['id']
                newFriend.name = str(resp_user['user']['profile']['real_name'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.username = str(resp_user['user']['name'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.image_url = resp_user['user']['profile']['image_48']
                newFriend.network_id = network_id
                newFriend.is_visible = 0
                newFriend.save()

                owner_friend_id = NetworkModel.Friend.select().order_by(NetworkModel.Friend.friend_id.desc()).get().friend_id

                currentNet.friend_id = owner_friend_id

            currentNet.user_id = session['user_id']
            currentNet.workspace = request.form['workspace']
            currentNet.oauth_access_token = request.form['oauth_access_token']
            currentNet.network_id = network_id
            currentNet.save()

            if slack_id == None:
                last_slack_id = NetworkModel.Slack.select().order_by(NetworkModel.Slack.slack_id.desc()).get().slack_id
                currentNetwork = NetworkModel.Network.get(NetworkModel.Network.network_id == network_id)
                currentNetwork.slack_id = last_slack_id
                currentNetwork.save()


            return redirect ('/slack?result=ok')

    else:
        return redirect ('/logout')


@app.route('/slack/new/<int:network_id>', methods=['GET', 'POST'])
def slackNew(network_id):
    return slackEdit(None, network_id)


# friends
@app.route('/slack/friends/<int:slack_id>', methods=['GET'])
def slackFriends(slack_id):
    if 'user_id' in session:
        form = FormList(request.form)
        currentNet = NetworkModel.Slack.get(NetworkModel.Slack.slack_id == slack_id)

        url = 'https://slack.com/api/users.list'

        headers = {
            'cache-control': "no-cache",
            'authorization': "Bearer " + currentNet.oauth_access_token
            }

        response = requests.request("GET", url, headers=headers)
        resp = json.loads(response.text)

        #print(json_str(resp))

        for friend in resp['members']:

            selectFriend= NetworkModel.Friend.select().where(NetworkModel.Friend.external_uuid == friend['id'], NetworkModel.Friend.network_id == currentNet.network_id)
            if selectFriend.count() == 0:
                newFriend = NetworkModel.Friend()
                newFriend.external_uuid = friend['id']
                newFriend.name = str(friend['profile']['real_name'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.username = str(friend['name'].encode('ascii', 'ignore').decode('utf-8', 'replace'))
                newFriend.image_url = friend['profile']['image_48']
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

        return render_template('slack/friends.html', form=form, twitter=currentNet, networks=friendList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type)
    else:
        return redirect ('/logout')


def conversation_open(users, oauth_access_token):
    url = "https://slack.com/api/conversations.open"

    payload = "'users': '{}'".format(users)
    payload = '{' + payload  + '}'

    headers = {
        'cache-control': "no-cache",
        'authorization': "Bearer " + oauth_access_token,
        'Content-Type': 'application/json;charset=utf-8'
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    resp = json.loads(response.text)
    #print(json_str(response.text))
    if resp['ok']:
        return resp['channel']['id']
    
    #print(response.text)
    return ''


#Messages
@app.route('/slack/<int:network_id>/friend/message/<int:friend_id>', methods=['GET', 'POST'])
def slackMessage(network_id, friend_id):
    if 'user_id' in session:
        currentFriend = NetworkModel.Friend.get(NetworkModel.Friend.network_id == network_id and NetworkModel.Friend.friend_id == friend_id )
        currentNet = NetworkModel.Slack.get(NetworkModel.Slack.network_id == network_id)

        form = FormEdit(request.form)

        if request.method == 'GET':
            return render_template('slack/message.html', form=form, friend=currentFriend)
        else:
            conversation_id = conversation_open(currentFriend.external_uuid, currentNet.oauth_access_token)

            url = "https://slack.com/api/chat.postMessage"

            payload = "'text': '{}', 'channel': '{}'".format(request.form['message'], conversation_id)
            payload = '{' + payload  + '}'
        
            headers = {
                'cache-control': "no-cache",
                'authorization': "Bearer " + currentNet.oauth_access_token,
                'Content-Type': 'application/json'

                }

            response = requests.request("POST", url, data=payload, headers=headers)
            resp = json.loads(response.text)

            if resp['ok']:
                return redirect ('/slack/inbox/' + str(network_id) + '/friend/' + str(currentFriend.friend_id) +'?result=ok')
            
            return redirect ('/slack/inbox/' + str(network_id) + '/friend/' + str(currentFriend.friend_id) +'?result=fail')

    else:
        return redirect ('/logout')



@app.route('/slack/inbox/<int:network_id>/friend/<int:friend_id>', methods=['GET'])
def slackMessageList(network_id, friend_id):
    if 'user_id' in session:
        form = FormList(request.form)
        currentNet = NetworkModel.Slack.get(NetworkModel.Slack.network_id == network_id)
        currentFriend = NetworkModel.Friend.get(NetworkModel.Friend.network_id == network_id and NetworkModel.Friend.friend_id == friend_id )
        conversation_id = conversation_open(currentFriend.external_uuid, currentNet.oauth_access_token)

        url = "https://slack.com/api/im.history?channel=" + conversation_id

        headers = {
            'cache-control': "no-cache",
            'authorization': "Bearer " + currentNet.oauth_access_token
            }

        response = requests.request("GET", url, headers=headers)
        resp = json.loads(response.text)

        #print(json_str(resp))

        for event in resp['messages']:
            
            selectMessage = NetworkModel.Message.select().where(NetworkModel.Message.external_uuid == event['user']+'-'+event['ts'], NetworkModel.Message.network_id == currentNet.network_id)

            if selectMessage.count() == 0:
                senderFriend = NetworkModel.Friend.select().where(NetworkModel.Friend.external_uuid == event['user'], NetworkModel.Friend.network_id == network_id)
                if senderFriend.count() == 0:
                    newFriend = NetworkModel.Friend()
                    newFriend.external_uuid = event['user']
                    newFriend.name = 'Desconocido'
                    newFriend.username = 'desconocido'
                    newFriend.network_id = network_id
                    newFriend.is_visible = 0
                    newFriend.save()

                    senderFriend = NetworkModel.Friend.select().where(NetworkModel.Friend.external_uuid == event['user'], NetworkModel.Friend.network_id == network_id)

          
                newMessage = NetworkModel.Message()
                newMessage.text = event['text']
                newMessage.external_uuid = event['user'] + '-' + event['ts']
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

        
        if resp['ok'] == False:
            show_message_css = ''
            show_message_type = 'danger'
            show_message_text = 'Error de API: ' + resp['error']

        return render_template('slack/inbox.html', form=form, slack=currentNet, networks=messageList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type)
    else:
        return redirect ('/logout')


@app.route('/slack/challenge/<string:workspace>/<int:slack_id>', methods=['POST', 'GET'])
def challenge(workspace, slack_id):
    currentNet = NetworkModel.Slack.select().where(NetworkModel.Slack.slack_id == slack_id, NetworkModel.Slack.workspace == workspace)
    if currentNet.count() == 1:
        if request.json['type'] == 'url_verification':
            response = {'challenge': request.json['challenge'] }
            return json.dumps(response)

        if request.json['event']['type'] == 'message':
            emisor = request.json['event']['user']
            canal = request.json['event']['channel']
            texto = request.json['event']['text']

        #send_msg('como va?' + emisor + ' - ' + texto, canal)

    return ''
