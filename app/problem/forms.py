#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField, IntegerField, ValidationError
from wtforms.validators import DataRequired
from flask import current_app


class SubmitForm(FlaskForm):

    '''
        define form of submitting code
    '''

    problem_id = IntegerField(u'题目ID', validators=[DataRequired()])
    language = SelectField(u'语言', coerce=int)
    code = TextAreaField(u'代码', validators=[DataRequired()])
    submit = SubmitField(u'提交')


    def validate_code(self, field):

        '''
            validate data of code field
        :param field: field
        :return: Null
        '''

        if len(field.data) < 10 or len(field.data) > 65535:
            raise ValidationError(u'代码长度必须在10到65535个字符之间')

    def __init__(self, *args, **kwargs):

        '''
            init function
        :param args: args
        :param kwargs: kwargs
        '''

        super(SubmitForm, self).__init__(*args, **kwargs)
        self.language.choices = [(current_app.config['LOCAL_LANGUAGE'][k], k)
                                 for k in current_app.config['LOCAL_LANGUAGE'].keys()]
