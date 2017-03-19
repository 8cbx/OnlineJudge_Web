#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time
from datetime import datetime
from app.models import Problem, OJList
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
        self.app_context.pop()

    def test_problem_add_new(self):

        '''
            test to insert into a new oj to database
        :return: None
        '''

        problem = Problem()
        db.session.add(problem)
        db.session.commit()
        self.assertTrue(Problem.query.count() == 1)

    def test_problem_in_oj(self):

        '''
            test for problem with oj is good
        :return: None
        '''

        oj = OJList(name='test')
        db.session.add(oj)
        db.session.commit()
        problem = Problem()
        problem.oj_id = oj.id
        db.session.add(problem)
        db.session.commit()
        self.assertTrue(problem.oj.name == 'test')

    def test_problem_after_delete_oj(self):

        '''
            test for ping func is good
        :return: None
        '''

        oj = OJList(name='test')
        db.session.add(oj)
        db.session.commit()
        problem = Problem()
        problem.oj_id = oj.id
        db.session.add(problem)
        db.session.commit()
        db.session.delete(oj)
        db.session.commit()
        self.assertTrue(Problem.query.count() == 0)

    def test_to_json(self):

        '''
            test for to_json func is good
        :return: None
        '''

        oj = OJList(name='test')
        db.session.add(oj)
        db.session.commit()
        problem = Problem(remote_id=1, oj_id=1, title='test')
        db.session.add(problem)
        db.session.commit()
        problem_json = problem.to_json()
        self.assertTrue(problem_json['id'] == 1)

    def test_from_json(self):

        '''
            test for from_json func is good
        :return: None
        '''

        problem_dict = {
            'remote_id': 1,
            'title': 'test',
            'description': 'test',
            'oj_id': 1,
        }
        problem = Problem().from_json(problem_dict)
        db.session.add(problem)
        db.session.commit()
        self.assertTrue(Problem.query.get(1).title == 'test')

    def test_from_json_false(self):

        '''
            test for from_json func is good
        :return: None
        '''

        problem_dict = {
            'remote_id': 1,
            'title': 'test',
            'description': 'test',
        }
        try:
            problem = Problem().from_json(problem_dict)
            db.session.add(problem)
            db.session.commit()
        except ValidationError:
            self.assertFalse(Problem.query.count() == 1)
