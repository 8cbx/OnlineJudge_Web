#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role
from app.index.views import gen_random_filename

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

    def test_404_page(self):

        '''
            test 404 page is good
        :return: None
        '''

        response = self.client.get(url_for('static', filename='styles.css'))
        self.assertTrue(response.status_code == 404)
        self.assertTrue(b'你要访问的页面去火星了' in response.data)

    def test_index_page(self):

        '''
            test index page is good
        :return: None
        '''

        response = self.client.get(url_for('index.index_page'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Welcome to HEU Online Judge' in response.data)

    def test_gen_random(self):

        '''
            test gen_random file name
        :return: None
        '''

        self.assertTrue(gen_random_filename() != gen_random_filename())

    def test_index_upload(self):

        '''
            test ckeditor upload func
        :return: None
        '''

        response = self.client.post(url_for('index.ckupload'))
        self.assertTrue(b'POST_ERROR' in response.data)
