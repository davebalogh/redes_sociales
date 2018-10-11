# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, Label
from wtforms.validators import DataRequired
from project.models import Login
from flask import flash


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
            flash('Usuario correcto', 'success')
        else:
            flash('Usuario o password incorrecta', 'error')
        
        return render_template('login/login.html', form=form)
    return render_template('login/login.html', form=form)


