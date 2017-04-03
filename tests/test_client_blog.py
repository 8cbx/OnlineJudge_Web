#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role, Blog

class FlaskClientTestCase(unittest.TestCase):

    def setUp(self):

        '''
            set up func for test model
        :return: None
        '''

        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):

        '''
            tear down func for test model
        :return: None
        '''

        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_blog_404(self):

        '''
            test 404 is good for problem
        :return: None
        '''

        response = self.client.get(url_for('blog.blog_list', page=123))
        self.assertTrue(response.status_code == 404)

    def test_blog_list(self):

        '''
            test status list is good
        :return: None
        '''

        response = self.client.get(url_for('blog.blog_list'))
        self.assertTrue(response.status_code == 200)
        u = User(username='tests', password='123456', email='test2@test.com', nickname='hahahaha', confirmed=True)
        db.session.add(u)
        db.session.commit()
        blog = Blog(title='BlogTitle', author_username='tests')
        db.session.add(blog)
        db.session.commit()
        response = self.client.get(url_for('blog.blog_list'))
        self.assertTrue(response.status_code == 200)
        self.assertFalse(b'BlogTitle' in response.data)
        response = self.client.get(url_for('blog.blog_detail', blog_id=1), follow_redirects=True)
        self.assertTrue(b'404' in response.data)
        blog.public = True
        db.session.add(blog)
        db.session.commit()
        response = self.client.get(url_for('blog.blog_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'BlogTitle' in response.data)
        response = self.client.get(url_for('blog.blog_detail', blog_id=1), follow_redirects=True)
        self.assertFalse(b'404' in response.data)
        self.assertTrue(b'BlogTitle' in response.data)
        u = User(username='test', password='123456', email='test@test.com', nickname='hahahaha', confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': '123456',
            'remember_me': 0
        }, follow_redirects=True)
        response = self.client.get(url_for('blog.blog_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'BlogTitle' in response.data)
        response = self.client.get(url_for('blog.blog_detail', blog_id=1), follow_redirects=True)
        self.assertFalse(b'404' in response.data)
        self.assertTrue(b'BlogTitle' in response.data)
        blog.public = False
        db.session.add(blog)
        db.session.commit()
        response = self.client.get(url_for('blog.blog_list'))
        self.assertTrue(response.status_code == 200)
        self.assertFalse(b'BlogTitle' in response.data)
        response = self.client.get(url_for('blog.blog_detail', blog_id=1), follow_redirects=True)
        self.assertTrue(b'404' in response.data)
        self.assertFalse(b'BlogTitle' in response.data)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('blog.blog_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'BlogTitle' in response.data)
        response = self.client.get(url_for('blog.blog_detail', blog_id=1), follow_redirects=True)
        self.assertFalse(b'404' in response.data)
        self.assertTrue(b'BlogTitle' in response.data)