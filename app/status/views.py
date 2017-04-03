#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, abort, current_app
from flask_login import login_required, current_user
from . import status
from .. import db
from ..models import SubmissionStatus, CompileInfo
from ..decorators import admin_required, permission_required
from datetime import datetime
import base64


@status.route('/', methods=['GET', 'POST'])
def status_list():

    '''
        define operations about showing status list
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    if current_user.is_admin():
        pagination = SubmissionStatus.query.order_by(SubmissionStatus.id.desc()).paginate(page,per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    else:
        pagination = SubmissionStatus.query.filter_by(visible=True).order_by(SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    status = pagination.items
    status_list = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]]=k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]]=k
    return render_template('status/status_list.html', status_list=status_list, language=language, status=status, pagination=pagination)


@status.route('/<int:run_id>', methods =['GET', 'POST'])
@login_required
def status_detail(run_id):

    '''
        define operations about showing status detail
    :param run_id: run_id
    :return: page
    '''

    status_detail = SubmissionStatus.query.filter_by(id=run_id).first_or_404()
    if status_detail.visible == False and not current_user.is_admin():
        return abort(404)
    if current_user.username != status_detail.author_username and (not current_user.is_admin()):
        return abort(403)
    code = base64.b64decode(status_detail.code).decode('utf-8')
    ce_info = CompileInfo.query.filter_by(submission_id=run_id).first()
    status_list = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    return render_template('status/status.html', status_list=status_list, language=language, status=status_detail, code=code, ce_info=ce_info)