# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, Label
from wtforms.validators import DataRequired
from project.models import Login
from flask import flash, session, redirect


#for user in Login.User.select():
#    print(user.username)



# https://wtforms.readthedocs.io/en/latest/index.html

class CreateFormList(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    
class CreateFormEdit(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


@app.route('/users', methods=['GET'])
def userList():
    if 'user_id' in session:
        form = CreateFormList(request.form)
        userList = Login.User.select()
        show_message = 'hide'
        if 'result' in request.args:
            show_message = ''

        return render_template('users/index.html', form=form, users=userList, message=show_message)
    else:
        return redirect ('/logout')


@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def userEdit(id=None):
    if 'user_id' in session:
        form = CreateFormEdit(request.form)
        currentUser = Login.User()
        if id != None:
            currentUser = Login.User.get(Login.User.user_id == id)

        if request.method == 'GET':
            if currentUser.user_id == None:
                currentUser = None

            return render_template('users/edit.html', form=form, user=currentUser)
        elif request.method == 'POST':

            currentUser.first_name = request.form['first_name']
            currentUser.last_name = request.form['last_name']
            currentUser.username = request.form['username']
            currentUser.email = request.form['email']
            currentUser.password = request.form['password']
            if request.form.get('is_admin', None) != None:
                currentUser.is_admin = 1
            else:
                currentUser.is_admin = 0
            if request.form.get('is_active', None) != None:
                currentUser.is_active = 1
            else:
                currentUser.is_active = 0
            print(currentUser.user_id)
            #validation of existing user
            existingUser = Login.User.select().where(Login.User.username == currentUser.username, Login.User.user_id != currentUser.user_id)
            print(existingUser.count())
            if existingUser.count() > 0:
                flash('Username exisitente', 'error')
                return render_template('users/edit.html', form=form, user=currentUser)
            else:
                currentUser.save()
                return redirect ('/users?result=ok')

    else:
        return redirect ('/logout')


@app.route('/users/new', methods=['GET', 'POST'])
def userNew():
    return userEdit(None)
    