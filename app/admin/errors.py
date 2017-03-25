#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template
from . import admin


@admin.app_errorhandler(403)
def forbidden(e):

    '''
        deal with forbidden request
    :param e:
    :return: pages
    '''

    return render_template('403.html'), 403


@admin.app_errorhandler(404)
def page_not_found(e):

    '''
        deal with page not found request
    :param e:
    :return: pages
    '''

    return render_template('404.html'), 404


@admin.app_errorhandler(500)
def internal_server_error(e):

    '''
        deal with server internal error
    :param e:
    :return: pages
    '''

    return render_template('500.html'), 500