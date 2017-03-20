#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time
from datetime import datetime
from app.models import Tag, Problem, TagProblem

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

    def test_insert_newtag(self):

        '''
            test to insert into a new tag to database
        :return: None
        '''

        tag = Tag()
        db.session.add(tag)
        db.session.commit()
        self.assertTrue(Tag.query.count() == 1)

    def test_tag_with_problem(self):

        '''
            test insert a tag with a problem
        :return: None
        '''

        tag = Tag()
        db.session.add(tag)
        db.session.commit()
        problem = Problem()
        db.session.add(problem)
        db.session.commit()
        problem_tag = TagProblem(tag=tag, problem=problem)
        db.session.add(problem_tag)
        db.session.commit()
        self.assertTrue(problem.tags.first().tag.id == tag.id)
        db.session.delete(tag)
        db.session.commit()
        self.assertTrue(problem.tags.count() == 0)
