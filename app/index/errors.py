#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, jsonify
from . import index


@index.app_errorhandler(403)
def forbidden(e):

    '''
        deal with forbidden request
    :param e:
    :return: pages
    '''

    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403


@index.app_errorhandler(404)
def page_not_found(e):

    '''
        deal with page not found request
    :param e:
    :return: pages
    '''

    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@index.app_errorhandler(500)
def internal_server_error(e):

    '''
        deal with server internal error
    :param e:
    :return: pages
    '''

    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500