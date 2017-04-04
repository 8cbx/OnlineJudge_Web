#!/usr/bin/env python
# -*- coding: utf-8 -*

from flask import jsonify
from app.exceptions import ValidationError
from . import api

def bad_request(message):

    '''
        deal with bad_request
    :param message:
    :return: josn_response
    '''

    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):

    '''
        deal with unauthorized request
    :param message:
    :return: josn_response
    '''

    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):

    '''
        deal with forbidden request
    :param message:
    :return: josn_response
    '''

    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def pending(message):

    '''
        deal with pendding request
    :param message:
    :return: josn_response
    '''

    response = jsonify({'error': 'pending', 'message': message})
    response.status_code = 200
    return response


@api.errorhandler(ValidationError)
def validation_error(e):

    '''
        deal with validation_error request
    :param message:
    :return: josn_response
    '''

    return bad_request(e.args[0])