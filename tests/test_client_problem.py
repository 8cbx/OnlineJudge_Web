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

    def test_problem_404(self):

        '''
            test 404 is good for problem
        :return: None
        '''

        response = self.client.get(url_for('problem.problem_detail', problem_id=123))
        self.assertTrue(response.status_code == 404)

    def test_problem_list(self):

        '''
            test problem list is good
        :return: None
        '''

        response = self.client.get(url_for('problem.problem_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Problem List' in response.data)
        self.assertFalse(b'thisisatest' in response.data)
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
        p.visible = False
        db.session.add(p)
        db.session.commit()
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('problem.problem_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Problem List' in response.data)
        self.assertTrue(b'thisisatest' in response.data)



    def test_problem_detail(self):

        '''
            test problem_detail is good
        :return: None
        '''

        p = Problem(title='test')
        db.session.add(p)
        db.session.commit()
        response = self.client.get(url_for('problem.problem_detail', problem_id=p.id))
        self.assertTrue(response.status_code == 404)
        p.visible = True
        db.session.add(p)
        db.session.commit()
        response = self.client.get(url_for('problem.problem_detail', problem_id=p.id))
        self.assertTrue(response.status_code == 200)

    def test_problem_submit(self):

        '''
            test problem submit is good
        :return: None
        '''

        p = Problem(title='test')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('problem.submit', problem_id=2), data={
            'problem_id': '2',
            'language': '1',
            'code': 'helloworldsdfsdf'
        })
        self.assertTrue(response.status_code == 302)
        u = User(username='test', password='test', email='test@test.com', nickname='hahahaha', confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'test',
            'remember_me': 0
        }, follow_redirects=True)
        response = self.client.post(url_for('problem.submit', problem_id=2), data={
            'problem_id': '2',
            'language': '1',
            'code': 'helloworldsdfsdf'
        })
        self.assertTrue(b'No such problem!' in response.data)
        response = self.client.post(url_for('problem.submit', problem_id=p.id), data={
            'problem_id': p.id,
            'language': '1',
            'code': 'helloworldsdfsdf'
        }, follow_redirects=True)
        self.assertTrue(b'No such problem!' in response.data)
        p.visible = True
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('problem.submit', problem_id=p.id), data={
            'problem_id': '1',
            'language': '1',
            'code': 'helloworldsdfsdf'
        })
        self.assertTrue(response.status_code == 302)
        p.visible = False
        db.session.add(p)
        db.session.commit()
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('problem.submit', problem_id=p.id), data={
            'problem_id': '1',
            'language': '1',
            'code': 'helloworldsdfsdf'
        })
        self.assertTrue(response.status_code == 302)
        response = self.client.post(url_for('problem.submit', problem_id=p.id), data={
            'problem_id': '1',
            'language': '1',
            'code': 'hellow'
        })
        self.assertTrue(b'代码长度必须在10到65535个字符之间' in response.data)
        response = self.client.get(url_for('problem.submit', problem_id=p.id))
        self.assertTrue(response.status_code == 200)
