# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, Label
from wtforms.validators import DataRequired
from project.models import NetworkModel
from flask import flash, session, redirect
import requests, json
from datetime import datetime

# https://wtforms.readthedocs.io/en/latest/index.html
# https://core.telegram.org/bots/api#userprofilephotos

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

@app.route('/telegram', methods=['GET'])
def telegramList():
    if 'user_id' in session:
        form = FormList(request.form)
        networkList = NetworkModel.Telegram.select()

        if session['is_admin'] != 1:
            networkList = NetworkModel.Telegram.select().where(NetworkModel.Telegram.user_id == session['user_id'])

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
        
        current_domain = request.headers.get('Host')

        if request.headers.get('X-Forwarded-Server') != None:
            current_domain = request.headers.get('X-Forwarded-Server') 
        
        return render_template('telegram/index.html', form=form, networks=networkList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type, url_domain = current_domain)
    else:
        return redirect ('/logout')

    

@app.route('/telegram/edit/<int:telegram_id>/<int:network_id>', methods=['GET', 'POST'])
def telegramEdit(telegram_id=None, network_id=None):
    if 'user_id' in session:
        form = FormEdit(request.form)
        currentNet = NetworkModel.Telegram()

        if telegram_id != None:
            currentNet = NetworkModel.Telegram.get(NetworkModel.Telegram.telegram_id == telegram_id)

        if request.method == 'GET':
            if currentNet.telegram_id == None:
                currentNet = None

            return render_template('telegram/edit.html', form=form, network=currentNet)

        elif request.method == 'POST':

            url = "https://api.telegram.org/bot"

            headers = {
                'Content-Type' : 'application/json'
            }

            response = requests.request("GET", url + request.form['bot_token'] + '/getMe', headers=headers)
            data = json.loads(response.text)

            if data['ok'] == False:
                flash('Bot Token inválido', 'error')
                currentNet.username = request.form['username']
                currentNet.bot_token = request.form['bot_token']
                return render_template('telegram/edit.html', form=form, network=currentNet)

            usernameTemp = request.form['username']
            if data['result']['username'] != usernameTemp:
                flash('El username no coincide. El token pertenece a: ' + data['result']['username'], 'error')
                currentNet.username = request.form['username']
                currentNet.bot_token = request.form['bot_token']
                return render_template('telegram/edit.html', form=form, network=currentNet)

            #creates default friend 
            if telegram_id == None:
                newFriend = NetworkModel.Friend()
                newFriend.external_uuid = data['result']['id']
                newFriend.name = data['result']['first_name']
                newFriend.username = data['result']['username']
                newFriend.network_id = network_id
                newFriend.is_visible = 0
                newFriend.save()

                owner_friend_id = NetworkModel.Friend.select().order_by(NetworkModel.Friend.friend_id.desc()).get().friend_id
                currentNet.webhook_activated = 0
                currentNet.friend_id = owner_friend_id

            currentNet.username = data['result']['username']
            currentNet.first_name = data['result']['first_name']
            currentNet.external_uuid = data['result']['id']
            currentNet.bot_token = request.form['bot_token']

            currentNet.user_id = session['user_id']
            currentNet.network_id = network_id
            currentNet.save()

            if telegram_id == None:
                last_telegram_id= NetworkModel.Telegram.select().order_by(NetworkModel.Telegram.telegram_id.desc()).get().telegram_id
                currentNetwork = NetworkModel.Network.get(NetworkModel.Network.network_id == network_id)
                currentNetwork.telegram_id = last_telegram_id
                currentNetwork.save()


            return redirect ('/telegram?result=ok')

    else:
        return redirect ('/logout')


@app.route('/telegram/new/<int:network_id>', methods=['GET', 'POST'])
def telegramNew(network_id):
    return telegramEdit(None, network_id)


#messages
@app.route('/telegram/inbox/<int:network_id>', methods=['GET'])
def telegramMessageList(network_id):
    if 'user_id' in session:
        form = FormList(request.form)
        currentNet = NetworkModel.Telegram.get(NetworkModel.Telegram.network_id == network_id)

        if currentNet.webhook_activated == 0:
            #import new messages
            url = "https://api.telegram.org/bot"

            headers = {
                'Content-Type' : 'application/json'
            }

            response = requests.request("GET", url + currentNet.bot_token + '/getUpdates', headers=headers)
            data = json.loads(response.text)

            if data['ok'] == True:
                for event in data['result']:
                    
                    selectMessage = NetworkModel.Message.select().where(NetworkModel.Message.external_uuid == event['message']['message_id'], NetworkModel.Message.network_id == currentNet.network_id)
                    
                    if 'text' in event['message'].keys() != None and selectMessage.count() == 0 and currentNet.friend_id.external_uuid != event['message']['from']['id']:
                        
                        senderFriend = NetworkModel.Friend.select().where(NetworkModel.Friend.external_uuid == event['message']['from']['id'], NetworkModel.Friend.network_id == network_id)
                        
                        if senderFriend.count() == 0:
                            newFriend = NetworkModel.Friend()
                            newFriend.external_uuid = event['message']['from']['id']
                            newFriend.name = event['message']['from']['first_name']
                            newFriend.username = event['message']['from']['first_name']
                            newFriend.network_id = network_id
                            newFriend.save()

                            senderFriend = NetworkModel.Friend.select().where(NetworkModel.Friend.external_uuid == event['message']['from']['id'], NetworkModel.Friend.network_id == network_id)

                        newMessage = NetworkModel.Message()
                        newMessage.text = event['message']['text']
                        newMessage.external_uuid = event['message']['message_id']
                        newMessage.network_id = network_id
                        newMessage.friend_sender_id = senderFriend[0].friend_id
                        newMessage.created_timestamp = datetime.utcfromtimestamp(int(event['message']['date'])) 
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

        return render_template('telegram/inbox.html', form=form, telegram=currentNet, networks=messageList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type)
    else:
        return redirect ('/logout')

@app.route('/telegram/<int:network_id>/friend/message/<int:friend_id>', methods=['GET', 'POST'])
def telegramMessage(network_id, friend_id):
    if 'user_id' in session:
        currentFriend = NetworkModel.Friend.get(NetworkModel.Friend.network_id == network_id and NetworkModel.Friend.friend_id == friend_id )
        currentNet = NetworkModel.Telegram.get(NetworkModel.Telegram.network_id == network_id)

        form = FormEdit(request.form)

        if request.method == 'GET':
            return render_template('telegram/message.html', form=form, friend=currentFriend)
        else:
            url = "https://api.telegram.org/bot"

            headers = {
                'Content-Type' : 'application/json'
            }

            payload = {'chat_id': currentFriend.external_uuid, 'text': request.form['message']}
            response = requests.request("POST", url + currentNet.bot_token + '/sendMessage', json=payload, headers=headers)
            data = json.loads(response.text)

            if data['ok']:
                return redirect ('/telegram/inbox/' + str(network_id) + '?result=ok')
            
            return redirect ('/telegram/inbox/' + str(network_id) + '?result=fail')

    else:
        return redirect ('/logout')



@app.route('/telegram/webhook/<int:telegram_id>/<string:webhook_state>', methods=['GET', 'POST'])
def telegramWebhook(telegram_id, webhook_state):
    if 'user_id' in session:

        currentNet = NetworkModel.Telegram.get(NetworkModel.Telegram.telegram_id == telegram_id)

        url = "https://api.telegram.org/bot"

        headers = {
            'Content-Type' : 'application/json'
        }

        current_domain = request.headers.get('Host')

        if request.headers.get('X-Forwarded-Server') != None:
            current_domain = request.headers.get('X-Forwarded-Server') 

        #http://{{url_domain}}/telegram/user/{{ network.user_id }}/bot/{{ network.telegram_id }}
        payload = {'url': 'http://' + current_domain + '/telegram/webhook/user/' + str(currentNet.user_id) + '/bot/' + str(currentNet.telegram_id)}

        webhook_method = ''

        if webhook_state == 'on':
            webhook_method = 'setWebHook'
        else:
            webhook_method = 'deleteWebhook'

        response = requests.request("POST", url + currentNet.bot_token + '/' + webhook_method, json=payload, headers=headers)
        data = json.loads(response.text)
        print(json_str(data))
        
        if data['ok']:
            currentNet.webhook_activated = 1
            currentNet.save()
            return redirect ('/telegram?result=ok')
            
        return redirect ('/telegram?result=fail')

    else:
        return redirect ('/logout')

# friends
@app.route('/telegram/friends/<int:telegram_id>', methods=['GET'])
def telegramFriends(telegram_id):
    if 'user_id' in session:
        form = FormList(request.form)
        currentNet = NetworkModel.Telegram.get(NetworkModel.Telegram.telegram_id == telegram_id)

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

        return render_template('telegram/friends.html', form=form, telegram=currentNet, networks=friendList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type)
    else:
        return redirect ('/logout')

