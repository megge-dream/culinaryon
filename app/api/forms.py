# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from flask import session
from wtforms import fields, validators, SubmitField, ValidationError
from werkzeug.security import check_password_hash
from app.api.users.model import User


class LoginForm(Form):
    email = fields.TextField(u"Адрес электронной почты")
    password = fields.PasswordField(u"Пароль")
    submit = SubmitField(u"Войти")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            raise ValidationError(u'Ошибка в адресе электронной почты или пароле.')