#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint

index = Blueprint('index', __name__)

from . import views, errors
from ..models import Permission

@index.app_context_processor
def inject_permissions():

    '''
        inject some special permission to permissions
    :return: dict
    '''

    return dict(Permission=Permission)
