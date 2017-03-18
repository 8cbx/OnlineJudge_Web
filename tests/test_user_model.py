#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time, os
from datetime import datetime
from app.models import Role, User

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
        Role.insert_roles()

    def tearDown(self):

        '''
            tear down func for test model
        :return: None
        '''

        db.session.remove()
        db.drop_all()
        files = os.listdir('./app/static/photo')
        for f in files:
            os.remove(os.path.join('./app/static/photo', f))
        self.app_context.pop()

    def test_user_role(self):

        '''
            test if user's default role is User
        :return: None
        '''

        u = User()
        self.assertTrue(u.role.name == 'User')

    def test_user_photo(self):

        '''
            test if user's photo can generate correctly
        :return: None
        '''

        u1 = User()
        u2 = User()
        self.assertTrue(u1.photo != u2.photo)

    def test_generate_auth_token(self):

        '''
            test if the User model can generate the correct auth token
        :return: None
        '''

        u = User()
        db.session.add(u)
        db.session.commit()
        self.assertTrue(u.generate_auth_token(expiration=3600))