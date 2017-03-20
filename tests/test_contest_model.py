#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time
from datetime import datetime
from app.models import Contest, ContestProblem, ContestUsers, Problem, User

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

    def test_contest_add_new(self):

        '''
            test to insert into a new contest to database
        :return: None
        '''

        contest = Contest()
        db.session.add(contest)
        db.session.commit()
        self.assertTrue(Contest.query.count() == 1)


    def test_contest_problem(self):

        '''
            test for add problem to contest is good
        :return: None
        '''

        contest = Contest()
        db.session.add(contest)
        db.session.commit()
        problem = Problem()
        db.session.add(problem)
        db.session.commit()
        contest_problem = ContestProblem(contest=contest, problem=problem)
        db.session.add(contest_problem)
        db.session.commit()
        self.assertTrue(contest.problems.first().problem.id == problem.id)
        db.session.delete(contest_problem)
        db.session.commit()
        self.assertTrue(contest.problems.count() == 0)

    def test_contest_user(self):

        '''
            test for add user to contest is good
        :return: None
        '''

        contest = Contest()
        db.session.add(contest)
        db.session.commit()
        user = User()
        db.session.add(user)
        db.session.commit()
        contest_user = ContestUsers(contest=contest, user=user)
        db.session.add(contest_user)
        db.session.commit()
        self.assertTrue(contest.users.first().user.id == user.id)
        db.session.delete(contest_user)
        db.session.commit()
        self.assertTrue(contest.users.count() == 0)


