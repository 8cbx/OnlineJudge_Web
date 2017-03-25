#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role

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

    def test_404_page(self):

        '''
            test 404 page is good
        :return: None
        '''

        response = self.client.get(url_for('static', filename='styles.css'))
        self.assertTrue(response.status_code == 404)
        self.assertTrue(b'你要访问的页面去火星了' in response.data)

    def test_index_page(self):

        '''
            test index page is good
        :return: None
        '''

        response = self.client.get(url_for('admin.admin_index'))
        self.assertTrue(response.status_code == 403)
        self.assertTrue(b'你要前往的页面需要特殊权限' in response.data)
        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        self.assertTrue(b'test2' in response.data)
        response = self.client.get(url_for('admin.admin_index'), follow_redirects=True)
        self.assertTrue(response.status_code == 403)
        self.assertTrue(b'你要前往的页面需要特殊权限' in response.data)
        u.role_id=Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('admin.admin_index'), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'test2' in response.data)