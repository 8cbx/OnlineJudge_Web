#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm as Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, PasswordField, DateField, \
    IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional, NumberRange
from wtforms import ValidationError
from ..models import Role, User, Permission, OJList, Problem, SubmissionStatus, CompileInfo, Contest, Logs, Tag
from flask import current_app


class PasswordRegisterForm(Form):

    '''
        define form of password register
    '''

    contest_password = StringField(u'比赛密码', validators=[DataRequired(), Length(0, 64)])
    submit = SubmitField(u'提交')


class SubmitForm(Form):

    '''
        define form of submit code
    '''
    language = SelectField(u'语言', coerce=int)
    code = TextAreaField(u'代码', validators=[DataRequired()])
    submit = SubmitField(u'提交')

    def validate_code(self, field):
        if len(field.data) < 10 or len(field.data) > 65535:
            raise ValidationError(u'代码长度必须在10到65535个字符之间')

    def __init__(self, *args, **kwargs):
        super(SubmitForm, self).__init__(*args, **kwargs)
        self.language.choices = [(current_app.config['LOCAL_LANGUAGE'][k], k)
                                 for k in current_app.config['LOCAL_LANGUAGE'].keys()]