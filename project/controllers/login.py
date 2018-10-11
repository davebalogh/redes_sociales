# -*- coding: utf-8 -*-
from project import app
from flask import render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from project.models import Login



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
        from project.models.Printer import Printer
        printer = Printer()
        printer.show_string(form.text.data)
        return render_template('login/index.html')
    return render_template('login/login.html', form=form)