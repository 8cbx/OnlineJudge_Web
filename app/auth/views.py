#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, redirect, request, url_for, flash, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User, Permission, SubmissionStatus, Follow
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm, EditProfileForm
from ..decorators import admin_required
from datetime import datetime

@auth.before_app_request
def before_request():

    '''
        define operation about before request
    :return: redirect page
    '''

    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():

    '''
        operation of unconfirmed user request
    :return: unconfirmed page
    '''

    if current_user.is_anonymous:
        abort(403)
    elif current_user.confirmed:
        abort(404)
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():

    '''
        define operation of user login
    :return: page
    '''

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # user login with correct password
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # log the admin login ip
            if user.is_admin() or user.is_super_admin():
                user.log_operation('Admin user login from ip %s' % request.headers.get('X-Real-IP'))
            return redirect(request.args.get('next') or url_for('index.index_page'))
        # admin user login with incorrect password
        if user is not None and (user.is_admin() or user.is_super_admin()):
            # log the login ip
            user.log_operation('Wrong password to login, login ip is %s' % request.headers.get('X-Real-IP'))
        flash(u'用户名或密码错误！')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():

    '''
        define operation of user logout
    :return: redirect page
    '''

    logout_user()
    flash(u'注销成功')
    return redirect(url_for('index.index_page'))


@auth.route('/register', methods=['GET', 'POST'])
def register():

    '''
        define operations of user registion
    :return: page
    '''

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        if current_app.config['SEND_EMAIL'] == True:
            token = user.generate_confirm_token()
            send_email.apply_async(args=[user.email, u'账号确认', 'auth/email/confirm', user.username, token])
            # send_email(user.email, u'账号确认', 'auth/email/confirm', user.username, token)
            login_user(user, False)
            flash(u'一封注册邮件已经发往您的邮箱，请点击确认连接进行确认！')
        else:
            login_user(user, False)
        return redirect(url_for('auth.unconfirmed'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):

    '''
        define operation of confirm user
    :param token: token
    :return: page
    '''

    if current_user.confirmed:
        return redirect(url_for('index.index_page'))
    if current_user.confirm(token):
        flash(u'感谢您确认了您的账号！')
        # return redirect(url_for('auth.edit_profile'))
        return redirect(url_for('index.index_page'))
    else:
        flash(u'确认链接无效或超过了最长的确认时间')
    return redirect(url_for('index.index_page'))


@auth.route('/confirm')
@login_required
def resend_confirmation():

    '''
        define operation of confirm user
    :return: page
    '''

    token = current_user.generate_confirm_token()
    send_email.apply_async(args=[current_user.email, 'Confirm Your Account', 'auth/email/confirm', current_user.username, token])
    flash(u'一封新的注册邮件已经发往您的邮箱，请点击确认连接进行确认！')
    return redirect(url_for('index.index_page'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():

    '''
        define operation of change password
    :return: page
    '''

    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'您的密码已经被更新！')
            return redirect(url_for('index.index_page'))
        else:
            flash(u'旧密码无效！')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():

    '''
        define request reset password operation
    :return: page
    '''

    if not current_user.is_anonymous:
        return redirect(url_for('index.index_page'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email.apply_async(args=[user.email, 'Reset your password', 'auth/email/reset_password', user.username, token])
            flash(u'一封重置密码的确认邮件已经发往您的邮箱，请点击连接进行密码重置！')
        else:
            flash(u'无效邮箱')
            return redirect(url_for('auth.password_reset_request'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):

    '''
        define operation of reset password
    :param token: token
    :return: page
    '''

    if not current_user.is_anonymous:
        return redirect(url_for('index.index_page'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.reset_password(token, form.password.data):
            flash(u'您的密码已经被更新')
            return redirect(url_for('auth.login'))
        else:
            flash(u'重置链接无效或超过了最长的重置时间')
            return redirect(url_for('index.index_page'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():

    '''
        define operation of change email request
    :return: page
    '''

    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email.apply_async(args=[new_email, 'Reset your email', 'auth/email/change_email', current_user.username, token])
            flash(u'一封修改邮箱的确认邮件已经发往您的旧邮箱，请点击连接进行邮箱修改操作！')
            return redirect(url_for('index.index_page'))
        else:
            flash(u'密码错误！')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):

    '''
        define operation of change email
    :param token: token
    :return: page
    '''

    if current_user.change_email(token):
        flash(u'您的邮箱已经被更新！')
    else:
        flash(u'重置邮箱链接无效或超过了最长的有效时间')
    return redirect(url_for('index.index_page'))


@auth.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_detail(username):

    '''
        define operation of showing user profile
    :param username: username
    :return: page
    '''

    user = User.query.filter_by(username = username).first_or_404()
    total_submission = SubmissionStatus.query.filter(SubmissionStatus.author_username==user.username).count()
    status = {}
    for k in current_app.config["LOCAL_SUBMISSION_STATUS"].keys():
        status[k] = SubmissionStatus.query.filter(SubmissionStatus.status==current_app.config['LOCAL_SUBMISSION_STATUS'][k], SubmissionStatus.author_username==user.username).count()
    return render_template('auth/user_detail.html', user=user, total_submission=total_submission, status=status)


@auth.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    '''
        define operation of editing profile
    :return: page
    '''

    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.realname = form.realname.data
        current_user.gender = form.gender.data
        current_user.major = form.major.data
        current_user.degree = form.degree.data
        current_user.country = form.country.data
        current_user.address = form.address.data
        current_user.school = form.school.data
        current_user.student_num = form.student_num.data
        current_user.phone_num = form.phone_num.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash(u'您的个人信息已经更新')
        return redirect(request.args.get('next') or url_for('auth.user_detail', username=current_user.username))
    form.nickname.data = current_user.nickname
    form.realname.data = current_user.realname
    form.gender.data = current_user.gender
    form.major.data = current_user.major
    form.degree.data = current_user.degree
    form.country.data = current_user.country
    form.address.data = current_user.address
    form.school.data = current_user.school
    form.student_num.data = current_user.student_num
    form.phone_num.data = current_user.phone_num
    form.about_me.data = current_user.about_me
    return render_template('auth/edit_profile.html', form=form)


@auth.route('/follow/<username>')
@login_required
def follow(username):

    '''
        define follow operations
    :param username: username
    :return:
    '''

    user = User.query.filter_by(username=username).first()
    if user is None or user.username==current_user.username:
        flash(u'无效用户名')
        return redirect(url_for('index.index_page'))
    if current_user.is_following(user):
        flash(u'你已经关注了这个用户！')
        return redirect(url_for('auth.user_detail', username=username))
    current_user.follow(user)
    flash(u'您从现在起关注了 %s.' % username)
    return redirect(url_for('auth.user_detail', username=username))


@auth.route('/unfollow/<username>')
@login_required
def unfollow(username):

    '''
        define operation of unfollow user
    :param username: username
    :return: page
    '''

    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效用户名')
        return redirect(url_for('index.index_page'))
    if not current_user.is_following(user):
        flash(u'你没有关注过这个用户！')
        return redirect(url_for('auth.user_detail', username=username))
    current_user.unfollow(user)
    flash(u'您从现在起不再关注 %s 了.' % username)
    return redirect(url_for('auth.user_detail', username=username))


@auth.route('/followed')
@login_required
def followed():

    '''
        define operation of showing followed user
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = current_user.followed.order_by(Follow.followed_id.asc()).paginate(page, per_page=current_app.config['FLASKY_USERS_PER_PAGE'])
    follows = pagination.items
    return render_template('auth/followed.html', follows=follows, pagination=pagination)


@auth.route('/followed_by')
@login_required
def followed_by():

    '''
        define operation of showing followed user
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    pagination = current_user.followers.order_by(Follow.follower_id.asc()).paginate(page, per_page=current_app.config['FLASKY_USERS_PER_PAGE'])
    follows = pagination.items
    return render_template('auth/followed_by.html', follows=follows, pagination=pagination)