#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_required, current_user
from . import problem
from .. import db
from ..models import SubmissionStatus, Problem
from datetime import datetime
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

    pass
    # problem = Problem.query.get_or_404(problem_id)
    # if problem.visible is False and (not current_user.is_admin()):
    #     abort(404)
    # return render_template('problem/problem.html', problem=problem)
