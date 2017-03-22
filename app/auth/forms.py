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


class RegistrationForm(FlaskForm):

    '''
        define register form
    '''

    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, u'用户名只能包含字母、数字和下划线，并且只能以字母开头')])
    password = PasswordField(u'密码', validators=[DataRequired(), EqualTo('password2', message=u'两次输入密码必须匹配')])
    password2 = PasswordField(u'密码确认', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):

        '''
            judge if the email has already registed
        :param field: field
        :return: Null
        '''

        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册')

    def validate_username(self, field):

        '''
            judge if the username has already registed
        :param field: field
        :return: Null
        '''

        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被注册')

    def validate_password(self, field):

        '''
            judge if the password length is bigger than 6
        :param field: field
        :return: Null
        '''

        if len(field.data) < 6:
            raise ValidationError(u'密码长度必须大于6位')