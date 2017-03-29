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
