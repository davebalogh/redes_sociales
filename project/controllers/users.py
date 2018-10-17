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
        currentUser = Login.User.get(Login.User.user_id == id)
        if request.method == 'GET':
            return render_template('users/edit.html', form=form, user=currentUser)
        elif request.method == 'POST':
            print(request.form)
            currentUser.first_name = request.form['first_name']
            currentUser.last_name = request.form['last_name']
            currentUser.username = request.form['username']
            currentUser.email = request.form['email']
            currentUser.password = request.form['password']
            currentUser.save()

            return redirect ('/users?result=ok')
    else:
        return redirect ('/logout')