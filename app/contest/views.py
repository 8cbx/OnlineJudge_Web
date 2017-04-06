#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import contest
from .. import db
from ..models import Role, User, Permission, OJList, Problem, SubmissionStatus, CompileInfo, Contest, Logs, Tag, ContestUsers, Topic
from .forms import PasswordRegisterForm, SubmitForm
from ..decorators import admin_required, permission_required
from datetime import datetime
import base64, time


def in_contest(contest, user_id):

    '''
        define operation of judging people is in contest
    :param contest: contest obj
    :param user_id: user.id
    :return: None
    '''

    user = contest.users.filter_by(user_id=user_id).first()
    if user is None:
        return False, redirect(url_for('contest.contest_detail', contest_id=contest.id))
    if user.user_confirmed == False:
        flash(u'请等待管理员确认您的参赛请求！')
        return False, redirect(url_for('contest.contest_detail', contest_id=contest.id))
    return True, None


@contest.route('/', methods=['GET', 'POST'])
def contest_list():

    '''
        define operation of contest_list
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Contest.query.filter_by(visible=True).order_by(Contest.id.desc()).paginate(page, per_page=current_app.config['FLASKY_CONTESTS_PER_PAGE'])
    contests = pagination.items
    now = datetime.utcnow()
    return render_template('contest/contest_list.html', contests=contests, pagination=pagination, now=now)


@contest.route('/<int:contest_id>', methods=['GET', 'POST'])
@login_required
def contest_detail(contest_id):

    '''
        define operation of showing a contest
    :param contest_id: contest id
    :return: page
    '''
    contest = Contest.query.get_or_404(contest_id)
    now = datetime.utcnow()
    is_in_contest = contest.users.filter_by(user_id=current_user.id).first()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if contest.manager_username == current_user.username or current_user.is_admin():
        if is_in_contest is None:
            return redirect(url_for('contest.open_contest_register', contest_id=contest_id))
        return render_template('contest/contest_detail.html', contest=contest, contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end)
    if is_in_contest is None:
        if contest.style == 1:
            return redirect(url_for('contest.open_contest_register', contest_id=contest_id))
        elif contest.style == 2 or contest.style == 4:
            flash(u'本场比赛为注册比赛，请先注册!')
            return redirect(url_for('contest.private_contest_pre_register', contest_id=contest_id))
        elif contest.style == 3:
            flash(u'本场比赛为密码认证比赛，请先输入密码进行认证!')
            return redirect(url_for('contest.password_contest_register', contest_id=contest_id))
        elif contest.style == 5:
            flash(u'本场比赛为正式比赛，您无权参加!')
            return redirect(url_for('contest.contest_list'))
    return render_template('contest/contest_detail.html', contest=contest ,contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end)


@contest.route('/<int:contest_id>/open_register', methods=['GET', 'POST'])
@login_required
def open_contest_register(contest_id):

    '''
        define operation of open contest register
    :param contest_id: contest_id
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    if contest.users.filter_by(user_id=current_user.id).first() is not None:
        flash(u'您已注册！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    contest_user = ContestUsers(
        user_id=current_user.id,
        contest_id=contest_id,
        realname=current_user.realname,
        address=current_user.address,
        school=current_user.school,
        student_num=current_user.student_num,
        phone_num=current_user.phone_num,
        user_confirmed=True,
        register_time=datetime.utcnow()
    )
    db.session.add(contest_user)
    db.session.commit()
    return redirect(url_for('contest.contest_detail', contest_id=contest_id))


@contest.route('/<int:contest_id>/private_pre_register', methods=['GET', 'POST'])
@login_required
def private_contest_pre_register(contest_id):

    '''
        define operation of private contest pre register
    :param contest_id: contest_id
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    if contest.users.filter_by(user_id=current_user.id).first() is not None:
        flash(u'您已注册！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    return render_template('contest/contest_private_register.html', contest=contest, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end, contest_id=contest_id)


@contest.route('/<int:contest_id>/private_register', methods=['GET', 'POST'])
@login_required
def private_contest_register(contest_id):

    '''
        define operation of private contest register
    :param contest_id: contest_id
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    if contest.users.filter_by(user_id=current_user.id).first() is not None:
        flash(u'您已注册！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    contest_user = ContestUsers(
        user_id=current_user.id,
        contest_id=contest_id,
        realname=current_user.realname,
        address=current_user.address,
        school=current_user.school,
        student_num=current_user.student_num,
        phone_num=current_user.phone_num,
        user_confirmed=True,
        register_time=datetime.utcnow()
    )
    db.session.add(contest_user)
    db.session.commit()
    flash(u'注册成功, 请等待比赛管理员同意您的参赛请求')
    return redirect(url_for('contest.contest_detail', contest_id=contest_id))


@contest.route('/<int:contest_id>/password_register', methods=['GET', 'POST'])
@login_required
def password_contest_register(contest_id):

    '''
        define operation of private contest pre register
    :param contest_id: contest_id
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if contest.users.filter_by(user_id=current_user.id).first() is not None:
        flash(u'您已注册！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    form = PasswordRegisterForm()
    if form.validate_on_submit():
        if form.contest_password.data == contest.password:
            contest_user = ContestUsers(
                user_id=current_user.id,
                contest_id=contest_id,
                realname=current_user.realname,
                address=current_user.address,
                school=current_user.school,
                student_num=current_user.student_num,
                phone_num=current_user.phone_num,
                user_confirmed=True,
                register_time=datetime.utcnow()
            )
            db.session.add(contest_user)
            db.session.commit()
            flash(u'注册成功!')
            return redirect(url_for('contest.contest_detail', contest_id=contest_id))
        else:
            flash(u'密码错误!')
            return redirect(url_for('contest.password_contest_register', contest_id=contest_id))
    return render_template('contest/contest_password_register.html', contest=contest, form=form, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end, contest_id=contest_id)


@contest.route('/<int:contest_id>/checking', methods=['GET', 'POST'])
@login_required
def contest_user_check(contest_id):

    '''
        define operation about admin confirm contest user
    :param contest_id: contest_id
    :return: page
    '''

    contest = Contest.query.get_or_404(contest_id)
    page = request.args.get('page', 1, type=int)
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if contest.manager_username != current_user.username and (current_user.is_admin() is False):
        flash(u"你没有权限访问这个页面！")
        abort(403)
    checked_num = contest.users.filter_by(user_confirmed=True).count()
    unchecked_num = contest.users.filter_by(user_confirmed=False).count()
    pagination = contest.users.order_by(ContestUsers.user_confirmed.asc(), ContestUsers.register_time.asc()).paginate(page, per_page=current_app.config['FLASKY_CONTESTS_PER_PAGE'])
    users = pagination.items
    return render_template('contest/contest_user_check.html', contest=contest, contest_id=contest_id, pagination=pagination, users=users, checked_num=checked_num, unchecked_num=unchecked_num, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end)


@contest.route('/<int:contest_id>/checked', methods=['GET', 'POST'])
@login_required
def contest_user_checked(contest_id):

    '''
        define operation about confirm or unconfirm user
    :param contest_id: contest_id
    :return: Null
    '''
    user_id = request.args.get('user_id', -1, type=int)
    flag = request.args.get('flag', 1, type=int)
    contest = Contest.query.get_or_404(contest_id)
    if contest.manager_username != current_user.username and (current_user.is_admin() is False):
        flash(u"你没有权限访问这个页面")
        abort(403)
    contest_user = ContestUsers.query.filter_by(user_id=user_id, contest_id=contest_id).first()
    if flag == 1:
        contest_user.user_confirmed = True
    else:
        contest_user.user_confirmed = False
    db.session.add(contest_user)
    db.session.commit()
    return redirect(url_for('contest.contest_user_check', contest_id=contest_id))


@contest.route('/<int:contest_id>/problems', methods=['GET', 'POST'])
@login_required
def contest_problem_list(contest_id):

    '''
        define operation about contest problem list
    :param contest_id: contest_id
    :return:
    '''
    contest = Contest.query.get_or_404(contest_id)
    now = datetime.utcnow()
    # is_in_contest = contest.users.filter_by(user_id=current_user.id).first()
    problems = contest.problems.all()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if contest.manager_username == current_user.username or current_user.is_admin():
        return render_template('contest/contest_problem_list.html', contest=contest, problems=problems, contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    if contest.start_time > now:
        flash(u'比赛尚未开始，请等待！')
        return redirect(url_for('contest.contest_detail',contest_id=contest_id))
    return render_template('contest/contest_problem_list.html', contest=contest, problems=problems ,contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end)


@contest.route('/<int:contest_id>/problem/<int:problem_index>', methods=['GET', 'POST'])
@login_required
def contest_problem_detail(contest_id, problem_index):

    '''
        define operation about showing contest problem detail
    :param contest_id: contest_id
    :param problem_index: problem_index
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if not result[0]:
        return result[1]
    problem = contest.problems.filter_by(problem_index=problem_index).first_or_404().problem
    if problem is None:
        return abort(404)
    return render_template('contest/contest_problem.html', contest=contest, problem=problem, problem_index=problem_index, contest_id=contest_id, sec_now = sec_now, sec_init = sec_init, sec_end = sec_end)


@contest.route('/<int:contest_id>/status', methods=['GET', 'POST'])
@login_required
def contest_status_list(contest_id):

    '''
        define operations about showing contest status
    :param contest_id: contest_id
    :return: page
    '''
    page = request.args.get('page', 1, type=int)
    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    pagination = SubmissionStatus.query.filter_by(contest_id=contest_id).order_by(SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    status = pagination.items
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    status_list = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    return render_template('contest/contest_status_list.html', status_list=status_list, language=language, status=status, pagination=pagination, contest_id=contest_id, contest=contest, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)


@contest.route('/<int:contest_id>/problem/<int:problem_index>/submit', methods=['GET', 'POST'])
@login_required
def contest_submit(contest_id, problem_index):

    '''
        define operation about submit code of the contest
    :param contest_id:
    :param problem_index:
    :return:
    '''

    form = SubmitForm()
    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    now = datetime.utcnow()
    if contest.end_time < now and current_user.username != contest.manager_username and (not current_user.is_admin()):
        flash(u'比赛已经结束，无法提交代码！')
        return redirect(url_for('contest.contest_detail', contest_id=contest_id))
    problem = contest.problems.filter_by(problem_index=problem_index).first_or_404().problem
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    if form.validate_on_submit():
        submission = SubmissionStatus(submit_time = datetime.utcnow(),
                                      problem_id = problem.id,
                                      status = 0,
                                      exec_time = 0,
                                      exec_memory = 0,
                                      code_length = len(form.code.data),
                                      language = form.language.data,
                                      code = base64.b64encode(form.code.data.encode('utf-8')),
                                      author_username = current_user.username,
                                      visible = False,
                                      contest_id = contest_id)
        db.session.add(submission)
        db.session.commit()
        return redirect(url_for('contest.contest_status_list',contest_id=contest_id))
    return render_template('contest/contest_submit.html', form=form, problem=problem, problem_index=problem_index, contest_id=contest_id, contest=contest, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)


@contest.route('/<int:contest_id>/status/<int:run_id>', methods=['GET', 'POST'])
@login_required
def contest_status_detail(run_id, contest_id):

    '''
        define operations of showing status detail
    :param run_id:
    :param contest_id:
    :return:
    '''

    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    status = contest.submissions.filter_by(id=run_id).first_or_404()
    if current_user.username != status.author_username and (not current_user.is_admin()):
        return abort(403)
    code=base64.b64decode(status.code).decode('utf-8')
    ce_info = CompileInfo.query.filter_by(submission_id=status.id).first()
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    status_list = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        status_list[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    return render_template('contest/contest_status_detail.html', status_list=status_list, language=language, status=status, code=code, ce_info=ce_info, contest_id=contest_id, contest=contest, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)


@contest.route('/<int:contest_id>/ranklist', methods=['GET', 'POST'])
@login_required
def contest_ranklist(contest_id):

    '''
        define operation of showing ranklist
    :param contest_id: contest_id
    :return: page
    '''

    '''
        data_struct:
        ranklist = [{username': (str), 'total_ac': (int), 'total_time': (int), 'submission_detail': {problem_index : {'submission_num': (int), 'ac': bool, 'first_blood': bool, 'time': (int)}}}]
    '''
    contest = Contest.query.get_or_404(contest_id)
    result = in_contest(contest, current_user.id)
    if not result[0]:
        return result[1]
    users = contest.users.all()
    problems = contest.problems.all()
    ranklists = []
    for user in users:
        if user.user.is_admin() or contest.manager_username==user.user.username:
            continue
        user_total = {}
        user_total['username'] = user.user.username
        user_total['submission_detail'] = {}
        user_total['total_time'] = 0
        user_total['total_ac'] = 0
        for problem in problems:
            status = contest.submissions.filter_by(problem_id=problem.problem_id, author_username=user_total['username']).order_by(SubmissionStatus.id.asc()).all()
            problem_detail = {}
            problem_detail['submission_num'] = 0
            problem_detail['ac'] = False
            problem_detail['first_blood'] = False
            problem_detail['time'] = 0
            for item in status:
                if item.status == 1:
                    problem_detail['ac'] = True
                    user_total['total_ac'] += 1
                    problem_detail['time'] = problem_detail['submission_num'] * 20 + (item.submit_time - contest.start_time).seconds / 60
                    user_total['total_time'] += problem_detail['time']
                    problem_detail['submission_num'] += 1
                    break
                else:
                    problem_detail['submission_num'] += 1
            user_total['submission_detail'][problem.problem_index] = problem_detail
        ranklists.append(user_total)
    for problem in problems:
        submissions = contest.submissions.filter_by(problem_id=problem.problem_id, status=current_app.config['LOCAL_SUBMISSION_STATUS']['Accepted']).order_by(SubmissionStatus.id.asc()).limit(20)
        for submission in submissions:
            for user_total in ranklists:
                if user_total['username'] == submission.author_username:
                    user_total['submission_detail'][problem.problem_index]['first_blood'] = True
                    break
    ranklists.sort(cmp=cmp_ranklist)
    now = datetime.utcnow()
    sec_now = time.mktime(now.timetuple())
    sec_init = time.mktime(contest.start_time.timetuple())
    sec_end = time.mktime(contest.end_time.timetuple())
    return render_template('contest/contest_ranklist.html', ranklists=ranklists, problems=problems, contest=contest, contest_id=contest_id, sec_now=sec_now, sec_init=sec_init, sec_end=sec_end)


def cmp_ranklist(a, b):

    '''
        define operation of cmp two ranklist item
    :param a: ranklist item
    :param b: ranklist item
    :return: bigger: -1, less: 1, equal 0
    '''

    if a['total_ac'] > b['total_ac']:
        return -1
    elif a['total_ac'] == b['total_ac']:
        if a['total_time'] < b['total_time']:
            return -1
        elif a['total_time'] == b['total_time']:
            return 0
        else:
            return 1
    else:
        return 1
