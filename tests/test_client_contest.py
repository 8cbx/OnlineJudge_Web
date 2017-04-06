#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role, Problem, Contest

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

    def test_contest_admin(self):

        '''
            test contest is good
        :return: None
        '''

        response = self.client.get(url_for('contest.contest_list'))
        self.assertTrue(response.status_code == 200)
        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 1 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        # add problem
        p = Problem(title='problem_test')
        db.session.add(p)
        db.session.commit()
        p = Problem(title='problem_test2')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '1',
            'problem_alias': 'contest_problem'
        }, follow_redirects=True)
        self.assertTrue(b'contest_problem' in response.data)
        # visit contest_detail
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'比赛描述' in response.data)
        # visit contest_problem list
        response = self.client.get(url_for('contest.contest_problem_list', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'contest_problem' in response.data)
        # visit contest problem detail
        response = self.client.get(url_for('contest.contest_problem_detail', contest_id=1, problem_index=1001), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'contest_problem' in response.data)
        # submit code
        response = self.client.post(url_for('contest.contest_submit', contest_id=1, problem_index=1001), data={
            'language': '1',
            'code': '1234567890.1234586789'
        },follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Waiting' in response.data)
        # visit contest status detail
        response = self.client.get(url_for('contest.contest_status_detail', run_id=1, contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Waiting' in response.data)
        # visit contest rank
        response = self.client.get(url_for('contest.contest_ranklist', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)


    def test_contest_user(self):

        '''
            test contest with normal user is good
        :return:
        '''

        response = self.client.get(url_for('contest.contest_list'))
        self.assertTrue(response.status_code == 200)
        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        # user login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        # add type 1 contest
        response = self.client.post(url_for('admin.contest_insert'), data={
            'contest_name': 'contest_test',
            'start_time': '2001-11-11 10:10',
            'end_time': '2001-11-11 10:11',
            'type': '1',
            'password': 'thisisatest',
            'manager': 'test2',
        }, follow_redirects=True)
        self.assertTrue(b'编辑比赛题目' in response.data)
        # add problem
        p = Problem(title='problem_test')
        db.session.add(p)
        db.session.commit()
        p = Problem(title='problem_test2')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('admin.add_contest_problem', contest_id=1), data={
            'problem_id': '1',
            'problem_alias': 'contest_problem'
        }, follow_redirects=True)
        self.assertTrue(b'contest_problem' in response.data)
        response = self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test3',
            'password': '123456'
        }, follow_redirects=True)
        # visit contest_detail
        response = self.client.get(url_for('contest.contest_detail', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'比赛描述' in response.data)
        # visit contest problem list
        response = self.client.get(url_for('contest.contest_problem_list', contest_id=1), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'contest_problem' in response.data)
        # visit contest problem detail
        response = self.client.get(url_for('contest.contest_problem_detail', contest_id=1, problem_index=1001),follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'contest_problem' in response.data)
        # submit code
        response = self.client.post(url_for('contest.contest_submit', contest_id=1, problem_index=1001), data={
            'language': '1',
            'code': '1234567890.1234586789'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'比赛已经结束' in response.data)