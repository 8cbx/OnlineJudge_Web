#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, BooleanField, SelectField, TextAreaField, SubmitField, IntegerField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, InputRequired
from wtforms import validators, ValidationError
from ..models import Role, User, Permission, OJList, Tag
from flask import current_app
from datetime import datetime


class ModifyProblem(FlaskForm):

    '''
        define form about Modify Problem
    '''

    problem_id = IntegerField(u'题目远程ID')
    oj_id = SelectField(u'题目所属OJ', coerce=int)
    title = StringField(u'标题', validators=[DataRequired()])
    time_limit = IntegerField(u'时间限制', validators=[DataRequired()])
    memory_limit = IntegerField(u'内存限制', validators=[DataRequired()])
    special_judge = BooleanField(u'Special Judge')
    submission_num = IntegerField(u'总提交数')
    accept_num = IntegerField(u'AC数')
    description = TextAreaField(u'题目描述')
    input = TextAreaField(u'输入')
    output = TextAreaField(u'输出')
    sample_input = TextAreaField(u'输入样例')
    sample_output = TextAreaField(u'输出样例')
    source_name = StringField(u'来源', validators=[Length(0, 64)])
    hint = TextAreaField(u'提示')
    author = StringField(u'作者', validators=[Length(0, 64)])
    visible = BooleanField(u'可见性')
    tags = SelectMultipleField(u'标签', coerce=int)
    submit = SubmitField(u'提交')


    def __init__(self, *args, **kwargs):

        '''
            init settings about ModifyProblem
        :param args: args
        :param kwargs: kwargs
        '''

        super(ModifyProblem, self).__init__(*args, **kwargs)
        self.oj_id.choices = [(oj.id, oj.name)
                              for oj in OJList.query.order_by(OJList.name).all()]
        self.tags.choices = [(tag.id, tag.tag_name)
                             for tag in Tag.query.order_by(Tag.tag_name).all()]


class ModifyTag(FlaskForm):

    '''
        define form about TagModify
    '''

    tag_name = StringField(u'标签名称', validators=[DataRequired(), Length(0, 32)])
    submit = SubmitField(u'提交')


class ModifyUser(FlaskForm):

    '''
        define form about ModifyUser
    '''

    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0, u'用户名只能包含字母、数字和下划线，并且只能以字母开头')])
    nickname = StringField(u'昵称', validators=[Length(0, 64)])
    confirmed = BooleanField(u'注册确认')
    role_id = SelectField(u'用户角色', coerce=int)
    gender = SelectField(u'性别', coerce=unicode)
    major = StringField(u'专业', validators=[Length(0, 64)])
    degree = SelectField(u'学位', coerce=unicode)
    country = SelectField(u'国家', coerce=unicode)
    address = StringField(u'通讯地址', validators=[Length(0, 128)])
    school = StringField(u'学校名称', validators=[Length(0, 128)])
    phone_num = StringField(u'手机号', validators=[Length(0, 32)])
    student_num = StringField(u'学号', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我', validators=[Length(0, 1024)])
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):

        '''
            init settings about ModifyUser class
        :param user: a user
        :param args: args
        :param kwargs: kwargs
        '''

        super(ModifyUser, self).__init__(*args, **kwargs)
        self.role_id.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user
        self.gender.choices = [(current_app.config['GENDER'][k][0], current_app.config['GENDER'][k][1])
                               for k in range(0, len(current_app.config['GENDER']))]
        self.degree.choices = [(current_app.config['DEGREE'][k][0], current_app.config['DEGREE'][k][1])
                               for k in range(0, len(current_app.config['DEGREE']))]
        self.country.choices = [(current_app.config['COUNTRY'][k][0], current_app.config['COUNTRY'][k][1])
                                for k in range(0, len(current_app.config['COUNTRY']))]

    def validate_email(self, field):

        '''
            judge the email field is good for our need
        :param field: field
        :return: None
        '''

        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已注册！')

    def validate_username(self, field):

        '''
            judge the username field is good for our need
        :param field: field
        :return: None
        '''

        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已注册！.')

