#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role, Problem

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

    def test_problem_list(self):

        '''
            test index page is good
        :return: None
        '''

        response = self.client.get(url_for('problem.problem_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Problem List' in response.data)
        self.assertFalse(b'test' in response.data)
        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        db.session.add(u)
        db.session.commit()
        p = Problem(title='thisisatest')
        db.session.add(p)
        db.session.commit()
        response = self.client.get(url_for('problem.problem_list'))
        self.assertFalse(b'thisisatest' in response.data)
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('problem.problem_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Problem List' in response.data)
        self.assertFalse(b'thisisatest' in response.data)
        p.visible = True
        db.session.add(p)
        db.session.commit()
        response = self.client.get(url_for('problem.problem_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Problem List' in response.data)
        self.assertTrue(b'thisisatest' in response.data)