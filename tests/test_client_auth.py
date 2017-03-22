#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role
import os, time

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
        u = User(username='test', password='test', nickname='hahahaha', confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'test'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'hahahaha' in response.data)

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
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'该账号尚未确认' in response.data)
        u.confirmed = True
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('auth.unconfirmed'))
        self.assertTrue(response.status_code == 404)
        self.assertTrue(b'你要访问的页面去火星了' in response.data)

    def test_log_out(self):

        '''
            test logout func is good
        :return: None
        '''

        u = User(username='test', password='test', nickname='hahahaha', confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'test'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'hahahaha' in response.data)
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertFalse(b'hahahaha' in response.data)

    def test_register_invaild(self):

        '''
            test register func is good
        :return: None
        '''

        # password does not match
        response = self.client.post(url_for('auth.register'), data={
            'email'     : 'test@test.com',
            'username'  : 'test',
            'password'  : '123456',
            'password2' : '12345'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'两次输入密码必须匹配' in response.data)

        # username vaild
        response = self.client.post(url_for('auth.register'), data={
            'email': 'test@test.com',
            'username': '8test',
            'password': '123456',
            'password2': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'用户名只能包含字母' in response.data)
        response = self.client.post(url_for('auth.register'), data={
            'email': 'test@test.com',
            'username': 'test+',
            'password': '123456',
            'password2': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'用户名只能包含字母' in response.data)

    def test_confirm(self):

        '''
            test confirm is good
        :return:
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
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'该账号尚未确认' in response.data)

        # confirm time out
        user = User.query.filter_by(username='test').first()
        token = user.generate_confirm_token(1)
        time.sleep(3)
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        self.assertTrue(b'确认链接无效或超过了最长的确认时间' in response.data)

        # confirm success
        token = user.generate_confirm_token()
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        self.assertTrue(b'感谢您确认了您的账号' in response.data)
