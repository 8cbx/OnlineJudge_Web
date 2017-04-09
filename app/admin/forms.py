#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, BooleanField, SelectField, TextAreaField, SubmitField, IntegerField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, InputRequired
from wtforms import validators, ValidationError
from ..models import Role, User, Permission, OJList, Tag, Contest
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

    def validate_tag_name(self, field):

        '''
            judge the email field is good for our need
        :param field: field
        :return: None
        '''

        if Tag.query.filter_by(tag_name=field.data).first():
            raise ValidationError(u'tag名称已存在！')


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


class ModifyOJStatus(FlaskForm):

    '''
        define Modify OJ status form
    '''

    oj_name = StringField(u'OJ名称', validators=[InputRequired(), Length(0, 128)])
    description = TextAreaField(u'OJ描述')
    url = StringField(u'OJ地址', validators=[InputRequired(), Length(0, 128)])
    vjudge = BooleanField(u'vjudge')
    status = SelectField(u'OJ状态', validators=[InputRequired()], choices=[('0', u'负载较重'), ('1', u'一般'), ('2', u'正常')])
    submit = SubmitField(u'提交')


class ModifySubmissionStatus(FlaskForm):

    '''
        define Modify submission status form
    '''

    status = SelectField(u'评判结果', validators=[InputRequired()], coerce=int)
    exec_time = IntegerField(u'运行时间', validators=[InputRequired()])
    exec_memory = IntegerField(u'运行内存', validators=[InputRequired()])
    visible = BooleanField(u'可见性')
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(ModifySubmissionStatus, self).__init__(*args, **kwargs)
        self.status.choices = [(int(current_app.config['LOCAL_SUBMISSION_STATUS'][k]), k)
                               for k in current_app.config['LOCAL_SUBMISSION_STATUS']]


class ModifyBlog(FlaskForm):

    '''
        define Modify Blog form
    '''

    title = StringField(u'标题', validators=[InputRequired(), Length(0, 64)])
    content = TextAreaField(u'内容', validators=[InputRequired()])
    public = BooleanField(u'可见性')
    submit = SubmitField(u'提交')


class ModifyContest(FlaskForm):

    '''
        define Modify Contest Form
    '''

    contest_name = StringField(u'比赛名称', validators=[DataRequired(), Length(0, 128)])
    start_time = DateTimeField(u'开始时间', format='%Y-%m-%d %H:%M')
    end_time = DateTimeField(u'结束时间', format='%Y-%m-%d %H:%M')
    type = SelectField(u'比赛类型', coerce=int, validators=[DataRequired()])
    password = StringField(u'比赛密码', validators=[Length(0, 64)])
    description = TextAreaField(u'比赛描述')
    announce = TextAreaField(u'比赛通知', validators=[Length(0, 1024)])
    visible = BooleanField(u'可见性')
    manager = StringField(u'管理员用户名', validators=[DataRequired()])
    rank_frozen = BooleanField(u'封榜')
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):

        '''
            init settings about ModifyContest class
        :param args: args
        :param kwargs: kwargs
        '''

        super(ModifyContest, self).__init__(*args, **kwargs)
        self.type.choices = [(1, u'开放注册'), (2, u'私有比赛(管理员确认)'), (3, u'私有比赛(密码保护)'), (4, u'现场赛预注册'), (5, u'现场赛/正式比赛')]

    def validate_manager(self, field):

        '''
            check if the manager is good
        :param field: form field
        :return: True or False
        '''

        if User.query.filter_by(username=field.data).first() is None:
            raise ValidationError(u'指定的比赛管理员用户不存在')


class AddContestProblem(FlaskForm):

    '''
        define Add contest problem form
    '''

    problem_id = IntegerField(u'题目ID', validators=[DataRequired()])
    problem_alias = StringField(u'题目别名', validators=[Length(0, 64)])
    submit = SubmitField(u'提交')


class ContestUserInsert(FlaskForm):

    '''
        define add contest user form
    '''

    user_list = TextAreaField(u'用户csv信息', validators=[DataRequired()])
    submit = SubmitField(u'提交')