#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time, os
from datetime import datetime
from app.models import Role, User, Permission, Follow, AnonymousUser, Logs

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
            if f[0] != '.':
                os.remove(os.path.join('./app/static/photo', f))
        self.app_context.pop()

    def test_user_role(self):

        '''
            test if user's default role is User
        :return: None
        '''

        u1 = User()
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.role.name == 'Super Administrator')
        u2 = User(email='1@qq.com')
        db.session.add(u2)
        db.session.commit()
        self.assertTrue(u2.role.name == 'User')


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
        self.assertTrue(u.generate_auth_token())

    def test_verify_auth_token(self):

        '''
            test if the verify func is good
        :return: None
        '''

        u = User()
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()
        self.assertTrue(u.verify_auth_token(token) == u)

    def test_no_password_getter(self):

        u = User()
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):

        '''
            test if the password varification is good
        :return: None
        '''
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):

        '''
            test if the salt is random
        :return: None
        '''

        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):

        '''
            test if the valid confirm token is good to use
        :return: None
        '''

        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirm_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):

        '''
            test if the invalid confim token is bad to use
        :return: None
        '''
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirm_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):

        '''
            test if the time expire bad to use the confirmation token
        :return: None
        '''

        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirm_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):

        '''
            test if the reset token is good to use to reset the password
        :return: None
        '''

        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))

    def test_invalid_reset_token(self):

        '''
            test if the reset token is bad to use a other token to reset the password
        :return: None
        '''

        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_reset_token()
        self.assertFalse(u2.reset_password(token, 'horse'))
        self.assertTrue(u2.verify_password('dog'))

    def test_valid_email_change_token(self):

        '''
            test for change email use token
        :return: None
        '''

        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('susan@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'susan@example.org')

    def test_invalid_email_change_token(self):

        '''
            test for change email using a invalid token
        :return: None
        '''

        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('david@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_duplicate_email_change_token(self):

        '''
            test for reset email with a used email
        :return: None
        '''

        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_roles_and_permissions(self):

        '''
            test for permimssions
        :return: None
        '''

        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(u.can(Permission.SUBMIT_CODE))
        self.assertFalse(u.can(Permission.EDIT_TAG))
        self.assertTrue(u.can(Permission.MODIFY_CONTEST))
        self.assertFalse(u.can(Permission.JUDGER))
        self.assertFalse(u.can(Permission.SUPER_ADMIN))

    def test_anonymous_user(self):

        '''
            test for anonymous User
        :return: None
        '''

        u = AnonymousUser()
        self.assertFalse(u.can(Permission.SUBMIT_CODE))

    def test_timestamps(self):

        '''
            test for time stamp is good
        :return: None
        '''

        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):

        '''
            test for ping func is good
        :return: None
        '''

        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)


    def test_follows(self):

        '''
            test for follow func
        :return: None
        '''

        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()
        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)
        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 0)
        self.assertTrue(u2.followers.count() == 0)
        self.assertTrue(Follow.query.count() == 0)
        u2.follow(u1)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 0)

    def test_log_operation(self):

        '''
            test user log func
        :return: None
        '''

        u = User()
        db.session.add(u)
        db.session.commit()
        u.log_operation("test")
        self.assertTrue(Logs.query.count() == 1)