#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, abort, flash, request, current_app,make_response
from flask_login import login_required, current_user
from datetime import datetime
from . import index
from .. import db
from ..models import Permission, KeyValue
from ..decorators import admin_required
import os, re, json, random, urllib, base64


@index.route('/', methods=['GET', 'POST'])
def index_page():

    '''
        deal with index route
    :return:
    '''

    return render_template('index.html')
