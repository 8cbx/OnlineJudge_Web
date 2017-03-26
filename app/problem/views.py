#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from . import problem
from .. import db
from ..models import SubmissionStatus, Problem
from datetime import datetime
from .forms import SubmitForm
import base64


@problem.route('/', methods=['GET', 'POST'])
def problem_list():

    '''
        show problem list operation
    :return: page
    '''
    page = request.args.get('page', 1, type=int)
    if current_user.is_admin():
        pagination = Problem.query.order_by(Problem.id.asc()).paginate(page, per_page=current_app.config['FLASKY_PROBLEMS_PER_PAGE'])
    else:
        pagination = Problem.query.filter_by(visible=True).order_by(Problem.id.asc()).paginate(page, per_page=current_app.config['FLASKY_PROBLEMS_PER_PAGE'])
    problems = pagination.items
    return render_template('problem/problem_list.html', problems=problems, pagination=pagination)


@problem.route('/<int:problem_id>', methods=['GET', 'POST'])
def problem_detail(problem_id):

    '''
        show problem details operation
    :param problem_id: problem_id
    :return: page
    '''

    problem = Problem.query.get_or_404(problem_id)
    if problem.visible is False and (not current_user.is_admin()):
        abort(404)
    return render_template('problem/problem.html', problem=problem)


@problem.route('/submit/<int:problem_id>', methods=['GET', 'POST'])
@login_required
def submit(problem_id):

    '''
        operation of submit code
    :param problem_id: problem_id
    :return: page
    '''

    submission = SubmissionStatus()
    form = SubmitForm()
    if form.validate_on_submit():
        problem = Problem.query.with_lockmode('update').get(form.problem_id.data)
        if problem is None or (problem.visible == False and not current_user.is_admin()):
            flash("No such problem!")
            return render_template('problem/submit.html', form=form)
        submission.submit_time = datetime.utcnow()
        submission.problem_id = form.problem_id.data
        submission.status = 0
        submission.time = 0
        submission.exec_memory = 0
        submission.language = form.language.data
        submission.code_length = len(form.code.data)
        submission.code = base64.b64encode(form.code.data.encode('utf-8'))
        submission.author_username = current_user.username
        submission.visible = True
        submission.submit_ip = request.headers.get('X-Real-IP')
        problem.submission_num += 1
        db.session.add(problem)
        db.session.add(submission)
        db.session.commit()
        #return redirect(url_for('status.status_list'))
        return redirect(url_for('index.index_page'))
    form.problem_id.data = problem_id
    return render_template('problem/submit.html', form=form)

