#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role, Problem, SubmissionStatus

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

    def test_status_404(self):

        '''
            test 404 is good for problem
        :return: None
        '''

        response = self.client.get(url_for('status.status_list', page=123))
        self.assertTrue(response.status_code == 404)

    def test_status_list(self):

        '''
            test status list is good
        :return: None
        '''

        response = self.client.get(url_for('status.status_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Status List' in response.data)
        self.assertFalse(b'Waiting' in response.data)
        p = Problem(title='test', visible=True)
        db.session.add(p)
        db.session.commit()
        u = User(username='test', password='test', email='test@test.com', nickname='hahahaha', confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'test',
            'remember_me': 0
        }, follow_redirects=True)
        response = self.client.post(url_for('problem.submit', problem_id=p.id), data={
            'problem_id': '1',
            'language': '1',
            'code': 'helloworldsdfsdf'
        })
        self.assertTrue(response.status_code == 302)
        response = self.client.get(url_for('status.status_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Status List' in response.data)
        self.assertTrue(b'Waiting' in response.data)
        response = self.client.get(url_for('status.status_detail', run_id=1))
        self.assertTrue(response.status_code == 200)
        s = SubmissionStatus.query.get(1)
        s.visible = False
        db.session.add(s)
        db.session.commit()
        response = self.client.get(url_for('status.status_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Status List' in response.data)
        self.assertFalse(b'Waiting' in response.data)
        response = self.client.get(url_for('status.status_detail', run_id=1), follow_redirects=True)
        self.assertTrue(b'404' in response.data)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('status.status_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Status List' in response.data)
        self.assertTrue(b'Waiting' in response.data)
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        u2 = User(username='test2', password='test', email='test2@test.com', nickname='hahahaha', confirmed=True)
        db.session.add(u2)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': 'test',
            'remember_me': 0
        }, follow_redirects=True)
        s = SubmissionStatus.query.get(1)
        s.visible = True
        db.session.add(s)
        db.session.commit()
        response = self.client.get(url_for('status.status_detail', run_id=1))
        self.assertTrue(response.status_code == 403)
        u2.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u2)
        db.session.commit()
        response = self.client.get(url_for('status.status_detail', run_id=1))
        self.assertTrue(response.status_code == 200)