#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time
from datetime import datetime
from app.models import Role

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

    def test_insert_role(self):

        '''
            test to insert into a new role to database
        :return: None
        '''

        r = Role(name="test", permission=0xff)
        db.session.add(r)
        db.session.commit()
        self.assertTrue(Role.query.count() == 1)

    def test_auto_insert(self):

        '''
            test insert_role func
        :return: None
        '''

        Role.insert_roles()
        self.assertTrue(Role.query.count() == 5)
