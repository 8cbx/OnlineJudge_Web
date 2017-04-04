#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import SubmissionStatus, Permission, CompileInfo, Problem
from . import api
from .decorators import permission_required
from ..exceptions import ValidationError
from .errors import pending


@api.route('/status/<int:status_id>')
@permission_required(Permission.JUDGER)
def get_status(status_id):

    '''
        define operation of get submission status
    :param id: submission id
    :return: status in json
    '''

    status = SubmissionStatus.query.get_or_404(status_id)
    return jsonify(status.to_json())


@api.route('/status/<int:status_id>/modify/', methods=['POST'])
@permission_required(Permission.JUDGER)
def change_status(status_id):

    '''
        define operation of change submission status
    :param id: submission id
    :return: status in json
    '''

    status = SubmissionStatus.query.get_or_404(status_id)
    new_status = SubmissionStatus.from_json(request.json)
    status.status = new_status.status
    status.exec_time = new_status.exec_time
    status.exec_memory = new_status.exec_memory
    db.session.add(status)
    db.session.commit()
    if status.status == 1:
        problem = Problem.query.with_lockmode('update').get(status.problem_id)
        problem.accept_num = problem.accept_num + 1
        db.session.add(problem)
        db.session.commit()
    return jsonify(status.to_json()), 201, \
           {'Location': url_for('api.get_status', status_id=status.id,
                                _external=True)}


@api.route('/status/<int:status_id>/ce_info/', methods=['POST', 'GET'])
@permission_required(Permission.JUDGER)
def add_ce_info(status_id):

    '''
        deal with operation of add compile error info
    :return: compile info in json
    '''

    submission = SubmissionStatus.query.get_or_404(status_id)
    ce_info = CompileInfo.from_json(request.json)
    ce_info.submission_id = submission.id
    db.session.add(ce_info)
    db.session.commit()
    return jsonify(ce_info.to_json()), 201, \
           {'Location': url_for('api.get_status', status_id=ce_info.submission_id,
                                _external=True)}


@api.route('/status/judge/', methods=['POST', 'GET'])
@permission_required(Permission.JUDGER)
def judge_new():

    '''
        deal with operation of judge new submission
    :return: submission in json
    '''

    status = SubmissionStatus.query.with_lockmode('update').filter_by(status=0).first()
    if status is None:
        db.session.commit()
        return pending("No more waiting submissions")
    status.status = 10
    db.session.add(status)
    db.session.commit()
    return jsonify(status.to_json())