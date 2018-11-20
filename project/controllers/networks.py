# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, Label
from wtforms.validators import DataRequired
from project.models import NetworkModel
from flask import flash, session, redirect



# https://wtforms.readthedocs.io/en/latest/index.html

class FormList(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class FormEdit(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

@app.route('/networks', methods=['GET'])
def networkList():
    if 'user_id' in session:
        form = FormList(request.form)
        networkList = NetworkModel.Network.select()

        if session['is_admin'] != 1:
            networkList = NetworkModel.Network.select().where(NetworkModel.Network.owner_id == session['user_id'])

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

        return render_template('networks/index.html', form=form, networks=networkList, message_css=show_message_css, message_text=show_message_text, message_type=show_message_type)
    else:
        return redirect ('/logout')

@app.route('/networks/edit/<int:id>', methods=['GET', 'POST'])
def networkEdit(id=None):
    if 'user_id' in session:
        form = FormEdit(request.form)
        currentNet = NetworkModel.Network()

        if id != None:
            currentNet = NetworkModel.Network.get(NetworkModel.Network.network_id == id)

        if request.method == 'GET':
            if currentNet.network_id == None:
                currentNet = None

            return render_template('networks/edit.html', form=form, network=currentNet)
        elif request.method == 'POST':
            currentNet.owner_id = session['user_id']
            currentNet.name = request.form['name']
            currentNet.network_type = request.form['network_type']
            if request.form.get('is_active', None) != None:
                currentNet.is_active = 1
            else:
                currentNet.is_active = 0

            currentNet.save()

            last_network_id = NetworkModel.Network.select().order_by(NetworkModel.Network.network_id.desc()).get().network_id


            if id == None:
                return redirect ('/' + currentNet.network_type.lower() + '/new/' + str(last_network_id))
            else:
                return redirect ('/networks?result=ok')

    else:
        return redirect ('/logout')


@app.route('/networks/new', methods=['GET', 'POST'])
def networkNew():
    return networkEdit(None)


@app.route('/networks/delete/<int:network_id>', methods=['GET', 'POST'])
def networkDelete(network_id):
    if 'user_id' in session:
        if network_id != None:
            currentNet = NetworkModel.Network.get(NetworkModel.Network.network_id == network_id)

            if currentNet.network_type == 'Twitter':
                currentTwitterNet = NetworkModel.Twitter.get(NetworkModel.Twitter.network_id == network_id)
                tweetList = NetworkModel.Tweet.delete().where(NetworkModel.Tweet.twitter_id == currentTwitterNet.twitter_id)
                friendList = NetworkModel.Friend.delete().where(NetworkModel.Friend.network_id == network_id)
                messageList = NetworkModel.Message.delete().where(NetworkModel.Message.network_id == network_id)

                if currentNet.network_id != None:
                    messageList.execute()
                    friendList.execute()
                    tweetList.execute()
                    currentTwitterNet.delete_instance()
                    currentNet.delete_instance()
                    return redirect ('/networks?result=ok')

            if currentNet.network_type == 'Slack':
                currentSlackNet = NetworkModel.Slack.get(NetworkModel.Slack.network_id == network_id)
                friendList = NetworkModel.Friend.delete().where(NetworkModel.Friend.network_id == network_id)
                messageList = NetworkModel.Message.delete().where(NetworkModel.Message.network_id == network_id)

                messageList.execute()
                friendList.execute()
                currentSlackNet.delete_instance()
                currentNet.delete_instance()

                return redirect ('/networks?result=ok')


            if currentNet.network_type == 'Telegram':
                currentTelegramNet = NetworkModel.Telegram.get(NetworkModel.Telegram.network_id == network_id)
                friendList = NetworkModel.Friend.delete().where(NetworkModel.Friend.network_id == network_id)
                messageList = NetworkModel.Message.delete().where(NetworkModel.Message.network_id == network_id)

                messageList.execute()
                friendList.execute()
                currentTelegramNet.delete_instance()
                currentNet.delete_instance()

                return redirect ('/networks?result=ok')

        return redirect ('/networks?result=fail')
    else:
        return redirect ('/logout')