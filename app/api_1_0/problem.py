#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from flask import jsonify, request, g, abort, url_for, current_app
from ..exceptions import ValidationError
from .. import db
from ..models import Problem, OJList, Permission
from . import api
from .decorators import permission_required

@api.route('/problem/<int:id>')
@permission_required(Permission.JUDGER)
def get_problem(id):

    '''
        deal with operation of getting problem detail with id
    :param id:  problem id
    :return: problem in json
    '''

    problem = Problem.query.get_or_404(id)
    return jsonify(problem.to_json())


@api.route('/problem/update/<int:oj_id>/<int:remote_id>/', methods=['POST'])
@permission_required(Permission.JUDGER)
def update_problem(oj_id, remote_id):

    '''
        deal with operation of insert problem detail with oj_id
    :param oj_id: oj_id
    :param remote_id: remote_id
    :return: None
    '''

    oj = OJList.query.filter_by(id=oj_id).first_or_404()
    problem_old = Problem.query.filter_by(oj_id=oj_id, remote_id=remote_id).first()
    problem_new = Problem.from_json(request.json)
    if not oj.vjudge:
        raise ValidationError('OJ is not vjudge!')
    if not problem_old:
        problem_old = Problem()
        problem_old.oj_id = problem_new.oj_id
        problem_old.remote_id = problem_new.remote_id
    elif problem_old.oj_id != problem_new.oj_id or problem_old.remote_id != problem_new.remote_id:
        raise ValidationError('Wrong oj_id or remote_id!')
    if problem_new.title:
        problem_old.title = problem_new.title
    if problem_new.time_limit:
        problem_old.time_limit = problem_new.time_limit
    if problem_new.memory_limit:
        problem_old.memory_limit = problem_new.memory_limit
    if problem_new.special_judge:
        problem_old.special_judge = problem_new.special_judge
    if problem_new.submission_num:
        problem_old.submission_num = problem_new.submission_num
    if problem_new.accept_num:
        problem_old.accept_num = problem_new.accept_num
    if problem_new.description:
        problem_old.description = problem_new.description
    if problem_new.input:
        problem_old.input = problem_new.input
    if problem_new.output:
        problem_old.output = problem_new.output
    if problem_new.sample_input:
        problem_old.sample_input = problem_new.sample_input
    if problem_new.sample_output:
        problem_old.sample_output = problem_new.sample_output
    if problem_new.source_name:
        problem_old.source_name = problem_new.source_name
    if problem_new.hint:
        problem_old.hint = problem_new.hint
    if problem_new.author:
        problem_old.author = problem_new.author
    if problem_new.last_update:
        problem_old.last_update = problem_new.last_update
    if problem_new.visible:
        problem_old.visible = problem_new.visible
    db.session.add(problem_old)
    db.session.commit()
    return jsonify(problem_old.to_json()), 201, \
        {'Location': url_for('api.get_problem', id=problem_old.id, _external=True)}