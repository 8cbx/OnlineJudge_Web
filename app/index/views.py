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


def gen_random_filename():

    '''
        random a filename for upload file
    :return: str(file_name)
    '''

    filename_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(100,10000)))


@index.route('/upload/', methods=['POST'])
def ckupload():

    '''
        CKEditor upload file function
    :return: response
    '''

    error = ''
    url = ''
    callback = request.args.get('CKEditorFuncNum')
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        random_name = '%s%s' % (gen_random_filename(), fext)
        filepath = os.path.join(current_app.static_folder, 'upload', random_name)
        dirname = os.path.dirname(filepath)
        # judge if the dir exist, if not create it
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        # judge if the dir writeable
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', random_name))
    else:
        error = 'POST_ERROR'
    res = """
        <script type="text/javascript">
            window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
        </script>
    """ % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response
