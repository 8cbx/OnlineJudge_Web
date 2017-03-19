#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time
from datetime import datetime
from app.models import OJList

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

    def test_ojlist_add_new(self):

        '''
            test to insert into a new oj to database
        :return: None
        '''

        oj = OJList(name='test')
        db.session.add(oj)
        db.session.commit()
        self.assertTrue(OJList.query.count() == 1)

    def test_ping(self):

        '''
            test for ping func is good
        :return: None
        '''

        oj = OJList(name='test')
        db.session.add(oj)
        db.session.commit()
        time.sleep(2)
        last_check_before = oj.last_check
        oj.ping()
        self.assertTrue(oj.last_check > last_check_before)

    def test_to_json(self):

        '''
            test for to_json func is good
        :return: None
        '''

        oj = OJList(name='test')
        db.session.add(oj)
        db.session.commit()
        oj_json = oj.to_json()
        self.assertTrue(oj_json['id'] == 1)
