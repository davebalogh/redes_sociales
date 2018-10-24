# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, Label
from wtforms.validators import DataRequired
from project.models import Login
from flask import flash, redirect, session


#for user in Login.User.select():
#    print(user.username)



# https://wtforms.readthedocs.io/en/latest/index.html

class CreateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    


@app.route('/', methods=['GET', 'POST'])
def login():
    form = CreateForm(request.form)
    if request.method == 'POST' and form.validate():
        query = Login.User.select().where(Login.User.username == form.username.data)
        if query.count() == 1 and query[0].password == form.password.data:
            #flash('Usuario correcto', 'success')

            if query[0].is_active != 1:
                flash('Usuario inactivo', 'error')
            else:
                session['user_id'] = query[0].user_id
                session['username'] = query[0].username
                session['is_admin'] = query[0].is_admin
                return redirect('/networks')
        else:
            flash('Usuario o password incorrecta', 'error')
        
        return render_template('login/login.html', form=form)
    return render_template('login/login.html', form=form)


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   session.pop('user_id', None)
   session.pop('is_admin', None)
   return redirect('/')