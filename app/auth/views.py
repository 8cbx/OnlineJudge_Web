#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User, Permission, SubmissionStatus, Follow
from ..email import send_email
from .forms import LoginForm
from ..decorators import admin_required
from datetime import datetime

@auth.before_app_request
def before_request():

    '''
        define operation about before request
    :return: redirect page
    '''

    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():

    '''
        operation of unconfirmed user request
    :return: unconfirmed page
    '''

    if current_user.is_anonymous:
        abort(403)
    elif current_user.confirmed:
        abort(404)
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():

    '''
        define operation of user login
    :return: page
    '''

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # user login with correct password
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # log the admin login ip
            if user.is_admin() or user.is_super_admin():
                user.log_operation('Admin user login from ip %s' % request.headers.get('X-Real-IP'))
            return redirect(request.args.get('next') or url_for('index.index_page'))
        # admin user login with incorrect password
        if user is not None and (user.is_admin() or user.is_super_admin()):
            # log the login ip
            user.log_operation('Wrong password to login, login ip is %s' % request.headers.get('X-Real-IP'))
        flash(u'用户名或密码错误！')
    return render_template('auth/login.html', form=form)