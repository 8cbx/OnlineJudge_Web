#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role

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

        response = self.client.get("127.0.0.1:5000/auth/logins")
        self.assertTrue(response.status_code == 404)
        self.assertTrue(b'你要访问的页面去火星了' in response.data)

    def test_login_page(self):

        '''
            test login page is good
        :return: None
        '''

        response = self.client.get(url_for('auth.login'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'登陆' in response.data)
        # wrong password
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'test',
            'remember_me': 0
        })
        self.assertTrue(b'用户名或密码错误' in response.data)
        # vaild username
        response = self.client.post(url_for('auth.login'), data={
            'username': '8test',
            'password': 'test',
            'remember_me': 0
        })
        self.assertTrue(b'用户名只能包含字母' in response.data)
        # right user
        u = User(username='test', password='test')
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'test'
        })
        self.assertTrue(response.status_code == 302)

    def test_unconfirmed_page(self):

        '''
            test unconfirmed page is good
        :return: None
        '''

        response = self.client.get(url_for('auth.unconfirmed'))
        self.assertTrue(b'你要前往的页面需要特殊权限' in response.data)
        u = User(username='test', password='test')
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'test',
            'remember_me': 0
        })
        self.assertTrue(response.status_code == 302)
        response = self.client.get(url_for('auth.unconfirmed'))
        self.assertTrue(b'该账号尚未确认' in response.data)
        u.confirmed = True
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('auth.unconfirmed'))
        self.assertTrue(response.status_code == 404)
        self.assertTrue(b'你要访问的页面去火星了' in response.data)
