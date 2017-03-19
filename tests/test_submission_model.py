#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time, os
from datetime import datetime
from app.models import Problem, SubmissionStatus, User
from app.exceptions import ValidationError

class UserModelTestCase(unittest.TestCase):

    def setUp(self):

        '''
            set up func for test model
        :return: None
        '''

        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):

        '''
            tear down func for test model
        :return: None
        '''

        db.session.remove()
        db.drop_all()
        files = os.listdir('./app/static/photo')
        for f in files:
            if f[0] != '.':
                os.remove(os.path.join('./app/static/photo', f))
        self.app_context.pop()

    def test_submission_add_new(self):

        '''
            test to insert into a new oj to database
        :return: None
        '''

        status = SubmissionStatus(code='test')
        db.session.add(status)
        db.session.commit()
        self.assertTrue(SubmissionStatus.query.count() == 1)

    def test_send_balloon(self):

        '''
            test for send_balloon func is good
        :return: None
        '''

        status = SubmissionStatus(code='test')
        db.session.add(status)
        db.session.commit()
        status.send_balloon()
        status = SubmissionStatus.query.get(1)
        self.assertTrue(status.balloon_sent == True)

    def test_to_json(self):

        '''
            test for to_json func is good
        :return: None
        '''

        problem = Problem()
        db.session.add(problem)
        db.session.commit()
        status = SubmissionStatus(problem_id=problem.id)
        db.session.add(status)
        db.session.commit()
        status = status.to_json()
        self.assertTrue(status['id'] == 1)

    def test_from_json(self):

        '''
            test for from json func is good
        :return: None
        '''

        status_dict = {
            'status': 1,
            'exec_time': '111',
            'exec_memory': '123',
        }
        status = SubmissionStatus().from_json(status_dict)
        db.session.add(status)
        db.session.commit()
        self.assertTrue(SubmissionStatus.query.get(1).exec_time == 111)

    def test_from_json_false(self):

        '''
            test for from_json func is good
        :return: None
        '''

        status_dict = {
            'status': 1,
            'exec_time': '111',
        }
        try:
            status = SubmissionStatus().from_json(status_dict)
            db.session.add(status)
            db.session.commit()
        except ValidationError:
            self.assertFalse(SubmissionStatus.query.count() == 1)

    def test_status_with_problem_delete(self):

        '''
            test for if the problem delete, status delete together
        :return: None
        '''

        problem = Problem()
        db.session.add(problem)
        db.session.commit()
        status = SubmissionStatus(problem_id=problem.id)
        db.session.add(status)
        db.session.commit()
        self.assertTrue(status.problem_id == problem.id)
        db.session.delete(problem)
        db.session.commit()
        self.assertTrue(SubmissionStatus.query.count() == 0)

    def test_status_with_user_delete(self):

        '''
            test for if the user delete, status delete together
        :return: None
        '''

        user = User(username='test')
        db.session.add(user)
        db.session.commit()
        status = SubmissionStatus(author_username=user.username)
        db.session.add(status)
        db.session.commit()
        self.assertTrue(status.author_username == user.username)
        db.session.delete(user)
        db.session.commit()
        self.assertTrue(SubmissionStatus.query.count() == 0)