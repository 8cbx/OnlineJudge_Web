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
        u.role=Role.query.filter_by(name='Administrator').first()
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'testt'
        }, follow_redirects=True)
        self.assertTrue(b'用户名或密码错误' in response.data)

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

        # confirm again
        token = user.generate_confirm_token()
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        self.assertFalse(b'感谢您确认了您的账号' in response.data)

    def test_change_password(self):

        '''
            test change password func is good
        :return: None
        '''

        u = User(username='test', password='testtest', confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'testtest',
            'remember_me': 0
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        # invalid old password
        response = self.client.post(url_for('auth.change_password'), data={
            'old_password': 'test1',
            'password': 'testtestt',
            'password2': 'testtestt'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'旧密码无效' in response.data)
        # valid old password
        response = self.client.post(url_for('auth.change_password'), data={
            'old_password': 'testtest',
            'password': 'testtestt',
            'password2': 'testtestt'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'您的密码已经被更新' in response.data)

    def test_reset_password(self):

        '''
            test request reset password func is good
        :return: None
        '''

        u = User(username='test', password='testtest', confirmed=True)
        db.session.add(u)
        db.session.commit()
        # login user redirect to index
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'testtest',
            'remember_me': 0
        }, follow_redirects=True)
        response = self.client.post(url_for('auth.password_reset_request'), data={
            'email': 'test@test.com'
        })
        self.assertTrue(response.status_code == 302)
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        response = self.client.post(url_for('auth.password_reset_request'), data={
            'email': 'test@test.com'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'无效邮箱' in response.data)

        # reset fail
        user = User.query.filter_by(username='test').first()
        token = user.generate_confirm_token()
        response = self.client.post(url_for('auth.password_reset', token=token), data={
            'email': 'test@test.com',
            'password': 'testtestt',
            'password2': 'testtestt'
        }, follow_redirects=True)
        self.assertTrue(b'无效邮箱' in response.data)

        # reset token time out
        user.email = 'test@test.com'
        db.session.add(user)
        db.session.commit()
        token = user.generate_reset_token(1)
        time.sleep(3)
        response = self.client.post(url_for('auth.password_reset', token=token), data={
            'email': 'test@test.com',
            'password': 'testtestt',
            'password2': 'testtestt'
        }, follow_redirects=True)
        self.assertTrue(b'重置链接无效或超过了最长的重置时间' in response.data)

        # reset success
        token = user.generate_reset_token()
        response = self.client.post(url_for('auth.password_reset', token=token), data={
            'email': 'test@test.com',
            'password': 'testtestt',
            'password2': 'testtestt'
        }, follow_redirects=True)
        self.assertTrue(b'您的密码已经被更新' in response.data)
        # login user redirect to index
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'testtestt',
            'remember_me': 0
        }, follow_redirects=True)
        token = user.generate_confirm_token()
        response = self.client.post(url_for('auth.password_reset', token=token), data={
            'email': 'test@test.com',
            'password': 'testtestt',
            'password2': 'testtestt'
        }, follow_redirects=True)
        self.assertFalse(b'您的密码已经被更新' in response.data)
        self.assertFalse(b'重置链接无效或超过了最长的重置时间' in response.data)
        self.assertFalse(b'无效邮箱' in response.data)


    def test_change_email(self):

        '''
            test change email func
        :return: None
        '''

        u = User(username='test', password='testtest', confirmed=True, email='test@test.com')
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'testtest',
            'remember_me': 0
        }, follow_redirects=True)
        response = self.client.post(url_for('auth.change_email_request'), data={
            'email': 'test@test.com',
            'password': 'testtest',
        }, follow_redirects=True)
        self.assertTrue(b'邮箱已被注册' in response.data)
        response = self.client.post(url_for('auth.change_email_request'), data={
            'email': 'testt@test.com',
            'password': 'testtestt',
        }, follow_redirects=True)
        self.assertTrue(b'密码错误' in response.data)

        # use good token test time out
        token = u.generate_email_change_token('testt@test.com', 1)
        time.sleep(3)
        response = self.client.get(url_for('auth.change_email', token=token), follow_redirects=True)
        self.assertTrue(b'重置邮箱链接无效或超过了最长的有效时间' in response.data)
        # test good token
        token = u.generate_email_change_token('testt@test.com')
        response = self.client.get(url_for('auth.change_email', token=token), follow_redirects=True)
        self.assertTrue(b'您的邮箱已经被更新' in response.data)
        self.assertTrue(User.query.get(1).email == 'testt@test.com')

    def test_user_detail(self):

        '''
            test user detail func
        :return: None
        '''

        u = User(username='test', password='testtest', confirmed=True, email='test@test.com', major='hahahaha')
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('auth.user_detail', username=u.username))
        self.assertFalse(b'hahahaha' in response.data)

        u2 = User(username='test2', password='testtest', confirmed=True, email='test2@test.com')
        db.session.add(u2)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': 'testtest'
        }, follow_redirects=True)
        response = self.client.get(url_for('auth.user_detail', username=u.username))
        self.assertTrue(b'hahahaha' in response.data)

        u.info_protection = True
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('auth.user_detail', username=u.username))
        self.assertFalse(b'hahahaha' in response.data)

        u2.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u2)
        db.session.commit()
        response = self.client.get(url_for('auth.user_detail', username=u.username))
        self.assertTrue(b'hahahaha' in response.data)

        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'testtest'
        }, follow_redirects=True)
        response = self.client.get(url_for('auth.user_detail', username=u.username))
        self.assertTrue(b'hahahaha' in response.data)

    def test_edit_profile(self):

        '''
            test if the edit user profile is good
        :return:
        '''

        u = User(username='test', password='testtest', confirmed=True, email='test@test.com', major='hahahaha')
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'testtest'
        }, follow_redirects=True)
        self.assertTrue(b'test' in response.data)
        response = self.client.post(url_for('auth.edit_profile'), data={
            'major': 'test2',
            'nickname': 'test2',
            'gender': 'Male',
            'degree': 'Bachelor',
            'country': 'China',
            'phone_num': '15555555555'
        }, follow_redirects=True)
        self.assertTrue(b'您的个人信息已经更新' in response.data)
        response = self.client.post(url_for('auth.edit_profile'), data={
            'major': 'test2',
            'phone_num': '155555555'
        }, follow_redirects=True)
        self.assertTrue(b'非法手机号' in response.data)

    def test_followed(self):

        '''
            test if the followed and followed_by func is good
        :return: None
        '''

        u1 = User(username='test', password='testtest', confirmed=True, email='test@test.com')
        db.session.add(u1)
        db.session.commit()
        u2 = User(username='test2', password='testtest', confirmed=True, email='test2@test.com')
        db.session.add(u2)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test',
            'password': 'testtest'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        response = self.client.get(url_for('auth.follow', username=u2.username), follow_redirects=True)
        self.assertTrue(b'您从现在起关注了' in response.data)
        response = self.client.get(url_for('auth.follow', username=u2.username), follow_redirects=True)
        self.assertTrue(b'你已经关注了这个用户' in response.data)
        response = self.client.get(url_for('auth.follow', username='testtt'), follow_redirects=True)
        self.assertTrue(b'无效用户名' in response.data)
        response = self.client.get(url_for('auth.follow', username='test'), follow_redirects=True)
        self.assertTrue(b'无效用户名' in response.data)
        response = self.client.get(url_for('auth.followed'), follow_redirects=True)
        self.assertTrue(b'test2' in response.data)
        response = self.client.get(url_for('auth.unfollow', username=u2.username), follow_redirects=True)
        self.assertTrue(b'您从现在起不再关注' in response.data)
        response = self.client.get(url_for('auth.unfollow', username='testtt'), follow_redirects=True)
        self.assertTrue(b'无效用户名' in response.data)
        response = self.client.get(url_for('auth.unfollow', username=u2.username), follow_redirects=True)
        self.assertTrue(b'你没有关注过这个用户' in response.data)
        response = self.client.get(url_for('auth.followed'), follow_redirects=True)
        self.assertFalse(b'test2' in response.data)
        u2.follow(u1)
        db.session.add(u2)
        db.session.commit()
        response = self.client.get(url_for('auth.followed_by'), follow_redirects=True)
        self.assertTrue(b'test2' in response.data)
        u2.unfollow(u1)
        db.session.add(u2)
        db.session.commit()
        response = self.client.get(url_for('auth.followed_by'), follow_redirects=True)
        self.assertFalse(b'test2' in response.data)