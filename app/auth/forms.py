#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired
from wtforms import ValidationError
from ..models import User
from flask import current_app

class LoginForm(FlaskForm):

    '''
        define login form
    '''

    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64),
                                               Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, u'用户名只能包含字母、数字和下划线，并且只能以字母开头')])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(u'记住我', default=False)
    submit = SubmitField(u'登陆')