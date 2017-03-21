#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user
from .models import Permission

def permission_required(permission):

    '''
        check for expect permissions
    :param permission:
    :return: decorator
    '''

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):

    '''
        check for admin permission
    :param f:
    :return: decorator
    '''

    return permission_required(Permission.ADMIN)(f)
