#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import admin
from .. import db
from ..models import Role, User, Permission, OJList, Problem, SubmissionStatus, CompileInfo, Contest, Logs, Tag, TagProblem, ContestUsers, ContestProblem, KeyValue
from werkzeug.utils import secure_filename
from ..decorators import admin_required, permission_required
from datetime import datetime, timedelta
import os, base64, json

@admin.route('/')
@admin_required
def admin_index():

    '''
        deal with the index page of admin part
    :return: page
    '''

    # Todo: need to optimized the query
    user_num = User.query.count()
    unconfirmed_user = User.query.filter_by(confirmed=0).count()
    oj_status = OJList.query.filter_by(status=0).count()
    online_user_num = User.query.filter('last_seen>:last_seen').params(last_seen=datetime.utcnow()-timedelta(minutes=1)).count()
    problem_num = Problem.query.count()
    submission_num = SubmissionStatus.query.count()
    contest_num = Contest.query.count()
    tag_num = Tag.query.count()
    judging_num = SubmissionStatus.query.filter_by(status=current_app.config['LOCAL_SUBMISSION_STATUS']['Judging']).count()
    waiting_num = SubmissionStatus.query.filter_by(status=current_app.config['LOCAL_SUBMISSION_STATUS']['Waiting']).count()
    return render_template('admin/index.html', user_num=user_num, unconfirmed_user=unconfirmed_user, oj_status=oj_status, online_user_num=online_user_num, problem_num=problem_num, submission_num=submission_num, contest_num=contest_num, tag_num=tag_num, judging_num=judging_num, waiting_num=waiting_num)


@admin.route('/problems', methods=['GET', 'POST'])
@admin_required
def problem_list():

    '''
        deal with the problem list page of admin part
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Problem.query.order_by(Problem.id.asc()).paginate(page, per_page=current_app.config['FLASKY_PROBLEMS_PER_PAGE'])
    problems = pagination.items
    return render_template('admin/problem_list.html', problems=problems, pagination=pagination)


@admin.route('/problem/<int:problem_id>', methods=['GET', 'POST'])
@admin_required
def problem_detail(problem_id):

    '''
        deal with the problem detail
    :param problem_id: problem id
    :return: page
    '''

    problem = Problem.query.get_or_404(problem_id)
    return render_template('admin/problem.html', problem=problem)