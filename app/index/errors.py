#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template
from . import index


@index.app_errorhandler(404)
def page_not_found(e):

    '''
        deal with page not found request
    :param e:
    :return: pages
    '''

    return render_template('404.html'), 404