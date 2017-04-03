#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, request, abort, current_app
from flask_login import login_required, current_user
from . import blog
from .. import db
from ..models import Blog
from ..decorators import admin_required, permission_required
from datetime import datetime
import base64

@blog.route('/', methods=['GET', 'POST'])
def blog_list():

    '''
        define operations about showing blog list
    :return: page
    '''

    page = request.args.get('page', 1, type=int)
    if current_user.is_admin():
        pagination = Blog.query.order_by(Blog.id.desc()).paginate(page,per_page=current_app.config['FLASKY_BLOGS_PER_PAGE'])
    else:
        pagination = Blog.query.filter_by(public=True).order_by(Blog.id.desc()).paginate(page, per_page=current_app.config['FLASKY_BLOGS_PER_PAGE'])
    blogs = pagination.items
    return render_template('blog/blog_list.html', blogs=blogs, pagination=pagination)

@blog.route('/<int:blog_id>', methods=['GET', 'POST'])
def blog_detail(blog_id):

    '''
        define operations about showing blog detail
    :return: page
    '''

    blog = Blog.query.get_or_404(blog_id)
    if blog.public == False and not current_user.is_admin():
        return abort(404)
    return render_template('blog/blog_detail.html', blog=blog)