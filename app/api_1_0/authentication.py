#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser, Permission
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):

    '''
        deal with operations of verify username and password or token
    :param username_or_token: username or token, depend on the password
    :param password: password or None
    :return: bool
    '''
    if username_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return (g.current_user is not None)
    user = User.query.filter_by(username=username_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    if not user.verify_password(password):
        return False
    if not g.current_user.can(Permission.JUDGER):
        return False
    return True


@auth.error_handler
def auth_error():

    '''
        deal with operation of error auth
    :return: error
    '''
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():

    '''
        deal with operation of request before
    :return:
    '''
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():

    '''
        deal with operation of getting newe token
    :return: token in json
    '''

    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
