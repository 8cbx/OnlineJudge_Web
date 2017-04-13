#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
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


class ChangePasswordForm(FlaskForm):

    '''
        define change password form
    '''

    old_password = PasswordField(u'旧密码', validators=[DataRequired()])
    password = PasswordField(u'新密码', validators=[DataRequired(), EqualTo('password2', message=u'两次输入密码必须匹配')])
    password2 = PasswordField(u'新密码确认', validators=[DataRequired()])
    submit = SubmitField(u'更新密码')

    def validate_password(self, field):

        '''
            judge if the password length is bigger than 6
        :param field: field
        :return: Null
        '''

        if len(field.data) < 6:
            raise ValidationError(u'密码必须大于6位')


class PasswordResetRequestForm(FlaskForm):

    '''
        define request password reset form
    '''

    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField(u'重置密码')


class PasswordResetForm(FlaskForm):

    '''
        define password reset form
    '''

    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'新密码', validators=[DataRequired(), EqualTo('password2', message=u'两次输入密码必须匹配')])
    password2 = PasswordField(u'新密码确认', validators=[DataRequired()])
    submit = SubmitField(u'重置密码')

    def validate_email(self, field):

        '''
            judge if the email is good to use
        :param field: field
        :return: Null
        '''

        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'无效邮箱')


class ChangeEmailForm(FlaskForm):

    '''
        define change email form
    '''

    email = StringField(u'新邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    submit = SubmitField(u"更新邮箱")

    def validate_email(self, field):

        '''
            judge if the email is good to use
        :param field: field
        :return: Null
        '''

        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册')


class EditProfileForm(FlaskForm):

    '''
        define edit profile form
    '''

    nickname = StringField(u'昵称', validators=[DataRequired(), Length(0, 64)])
    realname = StringField(u'真实姓名', validators=[Length(0, 64)])
    gender = SelectField(u'性别', coerce=unicode)
    major = StringField(u'专业', validators=[Length(0, 64)])
    degree = SelectField(u'学位', coerce=unicode)
    country = SelectField(u'国家', coerce=unicode)
    address = StringField(u'通讯地址', validators=[Length(0, 128)])
    school = StringField(u'学校', validators=[Length(0, 128)])
    student_num = StringField(u'学号', validators=[Length(0, 64)])
    phone_num = StringField(u'手机号', validators=[Length(0, 32), Regexp('0?(13|14|15|17|18)[0-9]{9}', 0, u'非法手机号')])
    about_me = TextAreaField(u'关于我', validators=[Length(0, 1024)])
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):

        '''
            init func to deal with the choices
        :param args: args
        :param kwargs: kwargs
        '''

        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.gender.choices = [(current_app.config['GENDER'][k][0], current_app.config['GENDER'][k][1])
                               for k in range(0, len(current_app.config['GENDER']))]
        self.degree.choices = [(current_app.config['DEGREE'][k][0], current_app.config['DEGREE'][k][1])
                               for k in range(0, len(current_app.config['DEGREE']))]
        self.country.choices = [(current_app.config['COUNTRY'][k][0], current_app.config['COUNTRY'][k][1])
                               for k in range(0, len(current_app.config['COUNTRY']))]
