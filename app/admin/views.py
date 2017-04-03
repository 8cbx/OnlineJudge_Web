#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import admin
from .. import db
from ..models import Role, User, Permission, OJList, Problem, SubmissionStatus, CompileInfo, Contest, Logs, Tag, TagProblem, ContestUsers, ContestProblem, KeyValue, Blog
from werkzeug.utils import secure_filename
from ..decorators import admin_required, permission_required
from datetime import datetime, timedelta
from .forms import ModifyProblem, ModifyTag, ModifyUser, ModifyOJStatus, ModifySubmissionStatus, ModifyBlog
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


@admin.route('/problem/insert', methods=['GET', 'POST'])
@admin_required
def problem_insert():

    '''
        deal with the insert problem operation
    :return: page
    '''

    problem = Problem()
    form = ModifyProblem()
    if form.validate_on_submit():
        if Problem.query.filter_by(oj_id=form.oj_id.data).order_by(Problem.remote_id.desc()).first() is None:
            problem.remote_id = 1
        else:
            problem.remote_id = Problem.query.filter_by(oj_id=form.oj_id.data).order_by(Problem.remote_id.desc()).first().id + 1
        problem.oj_id = form.oj_id.data
        problem.title = form.title.data
        problem.time_limit = form.time_limit.data
        problem.memory_limit = form.memory_limit.data
        problem.special_judge = form.special_judge.data
        problem.submission_num = form.submission_num.data
        problem.accept_num = form.accept_num.data
        problem.description = form.description.data
        problem.input = form.input.data
        problem.output = form.output.data
        problem.sample_input = form.sample_input.data
        problem.sample_output = form.sample_output.data
        problem.source_name = form.source_name.data
        problem.hint = form.hint.data
        problem.author = form.author.data
        problem.visible = form.visible.data
        for i in form.tags.data:
            t = TagProblem(tag=Tag.query.get(i), problem=problem)
            db.session.add(t)
            # db.session.commit()
        problem.last_update = datetime.utcnow()
        db.session.add(problem)
        db.session.commit()
        current_user.log_operation('Insert problem "%s", problem_id is %s' % (problem.title, str(problem.id)))
        return redirect(url_for('admin.problem_list'))
    form.oj_id.data =  problem.oj_id
    form.title.data = problem.title
    form.time_limit.data = problem.time_limit
    form.memory_limit.data = problem.memory_limit
    form.special_judge.data = problem.special_judge
    form.submission_num .data = problem.submission_num
    form.accept_num.data = problem.accept_num
    form.description.data = problem.description
    form.input.data = problem.input
    form.output.data = problem.output
    form.sample_input.data = problem.sample_input
    form.sample_output.data = problem.sample_output
    form.source_name.data = problem.source_name
    form.hint.data = problem.hint
    form.author.data = problem.hint
    form.visible.data = problem.visible
    form.tags.data = problem.tags
    return render_template('admin/problem_insert.html', form=form, problem=problem)


@admin.route('/problem/edit/<int:problem_id>', methods=['GET', 'POST'])
@admin_required
def problem_edit(problem_id):

    '''
        deal with the edit problem operation
    :param problem_id: problem_id
    :return:
    '''

    problem = Problem.query.get_or_404(problem_id)
    form = ModifyProblem()
    if form.validate_on_submit():
        problem.remote_id = form.problem_id.data
        problem.oj_id = form.oj_id.data
        problem.title = form.title.data
        problem.time_limit = form.time_limit.data
        problem.memory_limit = form.memory_limit.data
        problem.special_judge = form.special_judge.data
        problem.submission_num = form.submission_num.data
        problem.accept_num = form.accept_num.data
        problem.description = form.description.data
        problem.input = form.input.data
        problem.output = form.output.data
        problem.sample_input = form.sample_input.data
        problem.sample_output = form.sample_output.data
        problem.source_name = form.source_name.data
        problem.hint = form.hint.data
        problem.author = form.author.data
        problem.visible = form.visible.data
        # add tags to the problem, tag and problems are primary key, so it can't be duplicate
        for i in form.tags.data:
            t = TagProblem(tag=Tag.query.get(i), problems=problem)
            db.session.add(t)
            # db.session.commit()
        problem.last_update = datetime.utcnow()
        db.session.add(problem)
        db.session.commit()
        current_user.log_operation('Edit problem "%s", problem_id is %s' % (problem.title, str(problem.id)))
        return redirect(url_for('admin.problem_list'))
    form.problem_id.data = problem.remote_id
    form.oj_id.data = problem.oj_id
    form.title.data = problem.title
    form.time_limit.data = problem.time_limit
    form.memory_limit.data = problem.memory_limit
    form.special_judge.data = problem.special_judge
    form.submission_num.data = problem.submission_num
    form.accept_num.data = problem.accept_num
    form.description.data = problem.description
    form.input.data = problem.input
    form.output.data = problem.output
    form.sample_input.data = problem.sample_input
    form.sample_output.data = problem.sample_output
    form.source_name.data = problem.source_name
    form.hint.data = problem.hint
    form.author.data = problem.hint
    form.visible.data = problem.visible
    form.tags.data = problem.tags
    return render_template('admin/problem_edit.html', form=form, problem=problem)


@admin.route('/upload/<int:problem_id>', methods=['GET', 'POST'])
@admin_required
def upload_file(problem_id):

    '''
        deal with the input file list upload operation
    :param problem_id: problem_id
    :return: None
    '''

    problem = Problem.query.get_or_404(problem_id)
    if request.method == 'POST':
        if not os.path.exists(current_app.config['UPLOADED_PATH'] + str(problem_id) + '/'):
            os.makedirs(current_app.config['UPLOADED_PATH'] + str(problem_id) + '/')
        for f in request.files.getlist('file'):
            # print os.path.join(current_app.config['UPLOADED_PATH'] + str(problem_id) + '/', f.filename)
            f.save(os.path.join(current_app.config['UPLOADED_PATH'] + str(problem_id) + '/', f.filename))
    return render_template('admin/upload.html', problem_id=problem_id)


@admin.route('/tags', methods=['GET', 'POST'])
@admin_required
def tag_list():

    '''
        define tag list operations
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Tag.query.order_by(Tag.id.desc()).paginate(page, per_page=current_app.config['FLASKY_TAGS_PER_PAGE'])
    tags = pagination.items
    return render_template('admin/tag_list.html', tags=tags,  pagination=pagination)


@admin.route('/tag/edit/<int:tag_id>', methods=['GET', 'POST'])
@admin_required
def tag_edit(tag_id):

    '''
        define edit tag operation
    :param tag_id: tag id
    :return: page
    '''

    tag = Tag.query.get_or_404(tag_id)
    form = ModifyTag()
    if form .validate_on_submit():
        tag.tag_name = form.tag_name.data
        db.session.add(tag)
        db.session.commit()
        current_user.log_operation('Edit tag %s, tag_id is %s' % (tag.tag_name, str(tag.id)))
        flash('Tag update sucessful!')
        return redirect(url_for('admin.tag_list'))
    form.tag_name.data = tag.tag_name
    return render_template('admin/tag_edit.html', form=form)


@admin.route('/tag/add', methods=['GET', 'POST'])
@admin_required
def tag_insert():

    '''
        define add tag operation
    :return: page
    '''

    tag = Tag()
    form = ModifyTag()
    if form.validate_on_submit():
        tag.tag_name = form.tag_name.data
        db.session.add(tag)
        db.session.commit()
        current_user.log_operation('Add tag %s' % tag.tag_name)
        flash('Add tag sucessful!')
        return redirect(url_for('admin.tag_list'))
    form.tag_name.data = ''
    return render_template('admin/tag_edit.html', form=form)


@admin.route('/users', methods=['GET', 'POST'])
@admin_required
def user_list():

    '''
        deal with user list operation
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.asc()).paginate(page, per_page=current_app.config['FLASKY_USERS_PER_PAGE'])
    users = pagination.items
    return render_template('admin/user_list.html', users=users, pagination=pagination)


@admin.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):

    '''
        deal with user edit operation
    :param user_id: user_id
    :return: page
    '''

    user = User.query.get_or_404(user_id)
    form = ModifyUser(user)
    if form.validate_on_submit():
        if user.role.permission >= current_user.role.permission and current_user.username != user.username and current_user.role.permission != 0xff:
            current_user.log_operation(
                'Try to edit a high level permission user %s, user_id is %s' % (user.username, str(user.id)))
            flash(u"您无法编辑一个更高权限的用户!")
            return redirect(url_for('admin.user_list'))
        # if change to a high level role, the operation can not be exec
        elif Role.query.get_or_404(form.role_id.data).permission >= current_user.role.permission and current_user.role.permission != 0xff:
            current_user.log_operation(
                'Try to grant user %s a high level permission, user_id is %s' % (user.username, str(user.id)))
            flash(u"您不能给用户授予高于您本身的权限!")
            return redirect(url_for('admin.user_edit', user_id=user_id))
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.nickname = form.nickname.data
        user.gender = form.gender.data
        user.major = form.major.data
        user.degree = form.degree.data
        user.country = form.country.data
        user.address = form.address.data
        user.school = form.school.data
        user.student_num = form.student_num.data
        user.phone_num = form.phone_num.data
        user.about_me = form.about_me.data
        user.role_id = form.role_id.data
        db.session.add(user)
        db.session.commit()
        current_user.log_operation('Edit user %s, user_id is %s' % (user.username, str(user.id)))
        flash('Update successful!')
        return redirect(url_for('admin.user_list'))
    form.email.data = user.email
    form.username.data = user.username
    form.nickname.data = user.nickname
    form.confirmed.data = user.confirmed
    form.role_id.data = user.role_id
    form.gender.data = user.gender
    form.major.data = user.major
    form.degree.data = user.degree
    form.address.data = user.address
    form.country.data = user.country
    form.school.data = user.school
    form.student_num.data = user.student_num
    form.phone_num.data = user.phone_num
    form.about_me.data = user.about_me
    return render_template('admin/user_edit.html', form=form, user=user)


@admin.route('/user/<username>', methods=['GET', 'POST'])
@admin_required
def user_detail(username):

    '''
        define user detail operation
    :param username: username
    :return: page
    '''

    user = User.query.filter_by(username=username).first_or_404()
    return render_template('admin/user_detail.html', user=user)


@admin.route('/oj-status', methods=['GET', 'POST'])
@admin_required
def oj_list():

    '''
        define operations about showing oj list
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = OJList.query.order_by(OJList.id.asc()).paginate(page, per_page=current_app.config['FLASKY_OJS_PER_PAGE'])
    oj = pagination.items
    return render_template('admin/oj_list.html', oj=oj, pagination=pagination)


@admin.route('/oj-status/<int:oj_id>', methods=['GET', 'POST'])
@admin_required
def oj_status(oj_id):

    '''
        define operations about showing oj status
    :param oj_id: oj_id
    :return: page
    '''

    oj = OJList.query.get_or_404(oj_id)
    return render_template('admin/oj_detail.html', oj=oj)


@admin.route('/oj-status/edit/<int:oj_id>', methods=['GET', 'POST'])
@admin_required
def oj_status_edit(oj_id):

    '''
        define operations about editing oj status
    :param oj_id: oj_id
    :return: page
    '''

    oj = OJList.query.get_or_404(oj_id)
    form = ModifyOJStatus()
    if form.validate_on_submit():
        oj.name = form.oj_name.data
        oj.description = form.description.data
        oj.url = form.url.data
        oj.vjudge = form.vjudge.data
        oj.status = form.status.data
        db.session.add(oj)
        db.session.commit()
        current_user.log_operation('Edit oj %s Status, oj_id is %s' % (oj.name, str(oj.id)))
        flash('Update oj status successful!')
        return redirect(url_for('admin.oj_list'))
    form.oj_name.data = oj.name
    form.description.data = oj.description
    form.url.data = oj.url
    form.vjudge.data = oj.vjudge
    form.status.data = oj.status
    return render_template('admin/oj-status_edit.html', form=form, oj=oj)


@admin.route('/oj-status/add', methods=['GET', 'POST'])
@admin_required
def oj_status_insert():

    '''
        define operations about adding oj status
    :return: page
    '''

    oj = OJList()
    form = ModifyOJStatus()
    if form.validate_on_submit():
        oj.name = form.oj_name.data
        oj.description = form.description.data
        oj.url = form.url.data
        oj.vjudge = form.vjudge.data
        oj.status = form.status.data
        db.session.add(oj)
        db.session.commit()
        current_user.log_operation('Add oj %s, oj_id is %s' % (oj.name, str(oj.id)))
        flash('Add oj status successful!')
        return redirect(url_for('admin.oj_list'))
    return render_template('admin/oj-status_add.html', form=form)


@admin.route('/oj-status/delete', methods=['GET', 'POST'])
@admin_required
def oj_status_delete():

    '''
        define operations about deleting oj status
    :return: page
    '''

    # get problem_id from GET request
    oj_id = request.args.get('oj_id', -1, type=int)
    if oj_id != -1:
        oj = OJList.query.get(oj_id)
        if oj is not None:
            db.session.delete(oj)
            db.session.commit()
            current_user.log_operation('Delete oj %s, oj_id is %s' % (oj.name, str(oj.id)))
            flash('Delete oj successful!')
            return redirect(url_for('admin.oj_list'))
        else:
            flash('No such oj in oj_list!')
    else:
        flash('No such oj in oj_list!')
    return redirect(url_for('admin.oj_list'))


@admin.route('/submission-status', methods=['GET', 'POST'])
@admin_required
def submission_status_list():

    '''
        define operations about showing submission status
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = SubmissionStatus.query.order_by(SubmissionStatus.id.desc()).paginate(page, per_page=current_app.config['FLASKY_STATUS_PER_PAGE'])
    status = pagination.items
    submissions = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        submissions[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    return render_template('admin/submission_status_list.html', submissions=submissions, language=language, status=status, pagination=pagination)


@admin.route('/submission-status/<int:submission_id>', methods=['GET', 'POST'])
@admin_required
def submission_status_detail(submission_id):

    '''
        define submission status showing page
    :param submission_id: submission_id
    :return: page
    '''

    status_detail = SubmissionStatus.query.filter_by(id=submission_id).first_or_404()
    code = base64.b64decode(status_detail.code)
    ce_info = CompileInfo.query.filter_by(submission_id=submission_id).first()
    submissions = {}
    language = {}
    for k in current_app.config['LOCAL_SUBMISSION_STATUS'].keys():
        submissions[current_app.config['LOCAL_SUBMISSION_STATUS'][k]] = k
    for k in current_app.config['LOCAL_LANGUAGE'].keys():
        language[current_app.config['LOCAL_LANGUAGE'][k]] = k
    return render_template('admin/submission_status_detail.html', submissions=submissions, language=language, status=status_detail, code=code, ce_info=ce_info)


@admin.route('/submission-status/edit/<int:submission_id>', methods=['GET', 'POST'])
@admin_required
def submission_status_edit(submission_id):

    '''
        define operations about editing submission status
    :param submission_id: submission_id
    :return: page
    '''

    status_detail = SubmissionStatus.query.filter_by(id=submission_id).first_or_404()
    code = base64.b64decode(status_detail.code)
    ce_info = CompileInfo.query.filter_by(submission_id=submission_id).first()
    form = ModifySubmissionStatus()
    if form.validate_on_submit():
        status_detail.status = form.status.data
        status_detail.exec_time = form.exec_time.data
        status_detail.exec_memory = form.exec_memory.data
        status_detail.visible = form.visible.data
        return redirect(url_for('admin.submission_status_list'))
    form.status.data = status_detail.status
    form.exec_time.data = status_detail.exec_time
    form.exec_memory.data = status_detail.exec_memory
    form.visible.data = status_detail.visible
    return render_template('admin/submission_edit_status.html', status=status_detail, code=code, ce_info=ce_info, form=form)


@admin.route('/logs', methods=['GET', 'POST'])
@admin_required
def log_list():

    '''
        define operations about showing website log
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Logs.query.order_by(Logs.id.desc()).paginate(page, per_page=current_app.config['FLASKY_LOGS_PER_PAGE'])
    logs = pagination.items
    return render_template('admin/log_list.html', logs=logs, pagination=pagination)


@admin.route('/blogs', methods=['GET', 'POST'])
@admin_required
def blog_list():

    '''
        define operations about showing blog
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.order_by(Blog.id.desc()).paginate(page, per_page=current_app.config['FLASKY_BLOGS_PER_PAGE'])
    blogs = pagination.items
    return render_template('admin/blog_list.html', blogs=blogs, pagination=pagination)


@admin.route('/blog/add', methods=['GET', 'POST'])
@admin_required
def blog_insert():

    '''
        define operation about insert blog
    :return: page
    '''

    blog = Blog()
    form = ModifyBlog()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        blog.author_username = current_user.username
        blog.public = form.public.data
        db.session.add(blog)
        db.session.commit()
        current_user.log_operation('Add blog %s, blog_id is %s' % (blog.title, str(blog.id)))
        flash('Add blog successful!')
        return redirect(url_for('admin.blog_list'))
    return render_template('admin/blog_add.html', form=form)


@admin.route('/blog/edit/<int:blog_id>', methods=['GET', 'POST'])
@admin_required
def blog_edit(blog_id):

    '''
        define operation about edit blog
    :return: page
    '''

    blog = Blog.query.get_or_404(blog_id)
    form = ModifyBlog()
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        blog.author_username = current_user.username
        blog.public = form.public.data
        blog.last_update = datetime.utcnow()
        db.session.add(blog)
        db.session.commit()
        current_user.log_operation('Edit blog %s, blog_id is %s' % (blog.title, str(blog.id)))
        flash('Edit blog successful!')
        return redirect(url_for('admin.blog_list'))
    form.title.data = blog.title
    form.content.data = blog.content
    form.public.data = blog.public
    return render_template('admin/blog_edit.html', form=form)


@admin.route('/blog/<int:blog_id>', methods=['GET', 'POST'])
@admin_required
def blog_detail(blog_id):

    '''
        define operation about blog detail
    :param blog_id: blog_id
    :return: page
    '''

    blog = Blog.query.get_or_404(blog_id)
    return render_template('admin/blog_detail.html', blog=blog)
