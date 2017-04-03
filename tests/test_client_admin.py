#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import User, Role, Problem, OJList

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

        response = self.client.get(url_for('admin.admin_index'))
        self.assertTrue(response.status_code == 403)
        self.assertTrue(b'你要前往的页面需要特殊权限' in response.data)
        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        self.assertTrue(b'test2' in response.data)
        response = self.client.get(url_for('admin.admin_index'), follow_redirects=True)
        self.assertTrue(response.status_code == 403)
        self.assertTrue(b'你要前往的页面需要特殊权限' in response.data)
        u.role_id=Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.get(url_for('admin.admin_index'), follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'test2' in response.data)

    def test_problem_list(self):

        '''
            test admin problem_list is good
        :return: None
        '''

        response = self.client.get(url_for('admin.problem_list'))
        self.assertTrue(response.status_code == 403)
        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        p = Problem(title='thisisatest')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.problem_list'))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'Problem List' in response.data)
        self.assertTrue(b'thisisatest' in response.data)

    def test_problem_detail(self):

        '''
            test admin problem detail page is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        p = Problem(title='thisisatest')
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.problem_detail', problem_id=p.id))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'thisisatest' in response.data)

    def test_add_problem(self):

        '''
            test admin add problem page is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        oj = OJList(name='local')
        db.session.add(oj)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.problem_insert'))
        response = self.client.post(url_for('admin.problem_insert'), data={
            'oj_id': '1',
            'title': 'hahah',
            'time_limit': '1',
            'memory_limit': '1'
        }, follow_redirects=True)
        self.assertTrue(b'hahah' in response.data)

    def test_edit_problem(self):

        '''
            test admin add problem page is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        oj = OJList(name='local')
        db.session.add(oj)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.problem_insert'))
        response = self.client.post(url_for('admin.problem_insert'), data={
            'oj_id': '1',
            'title': 'hahah',
            'time_limit': '1',
            'memory_limit': '1'
        }, follow_redirects=True)
        self.assertTrue(b'hahah' in response.data)
        response = self.client.get(url_for('admin.problem_edit', problem_id=1))
        self.assertTrue(b'hahah' in response.data)
        response = self.client.post(url_for('admin.problem_edit', problem_id=1), data={
            'oj_id': '1',
            'title': 'hahahhaha',
            'time_limit': '1',
            'memory_limit': '1'
        }, follow_redirects=True)
        self.assertTrue(b'hahahhaha' in response.data)

    def test_upload_file(self):

        '''
            test upload file
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        oj = OJList(name='local')
        db.session.add(oj)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.upload_file', problem_id=1))
        self.assertTrue(response.status_code == 404)
        response = self.client.post(url_for('admin.problem_insert'), data={
            'oj_id': '1',
            'title': 'hahah',
            'time_limit': '1',
            'memory_limit': '1'
        }, follow_redirects=True)
        response = self.client.get(url_for('admin.upload_file', problem_id=1))
        self.assertTrue(response.status_code == 200)
        response = self.client.post(url_for('admin.upload_file', problem_id=1))
        self.assertTrue(response.status_code == 200)

    def test_tag(self):

        '''
            test tag part
        :return: None
        '''

        u = User(username='test2', password='123456', email='test@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.post(url_for('admin.tag_insert'), data={
            'tag_name': 'thisisatag'
        }, follow_redirects=True)
        self.assertTrue(b'thisisatag' in response.data)
        response = self.client.post(url_for('admin.tag_edit', tag_id=1), data={
            'tag_name': 'thisisatag2'
        }, follow_redirects=True)
        self.assertTrue(b'thisisatag2' in response.data)

    def test_edit_user(self):

        '''
            test user part
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        u2 = User(username='test3', password='123456', email='test3@test.com', confirmed=True)
        db.session.add(u2)
        db.session.commit()
        response = self.client.get(url_for('admin.user_list'))
        self.assertTrue(b'test3' in response.data)
        response = self.client.get(url_for('admin.user_detail', username=u2.username))
        self.assertTrue(b'test3' in response.data)
        response = self.client.get(url_for('admin.user_edit', user_id=u2.id))
        self.assertTrue(b'test3' in response.data)
        response = self.client.post(url_for('admin.user_edit', user_id=u2.id), data={
            'email': 'test4@test.com',
            'username': 'test3',
            'role_id': Role.query.filter_by(permission=0x11).first().id,
            'gender': 'Male',
            'degree': 'Bachelor',
            'country': 'China'
        }, follow_redirects=True)
        self.assertTrue(b'test4' in response.data)
        u.role_id = Role.query.filter_by(permission=0x40).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('admin.user_edit', user_id=u2.id), data={
            'email': 'test14@test.com',
            'username': 'test3',
            'role_id': Role.query.filter_by(permission=0x11).first().id,
            'gender': 'Male',
            'degree': 'Bachelor',
            'country': 'China'
        }, follow_redirects=True)
        self.assertTrue(b'test14' in response.data)
        u2.role_id = Role.query.filter_by(permission=0x40).first().id
        db.session.add(u2)
        db.session.commit()
        response = self.client.post(url_for('admin.user_edit', user_id=u2.id), data={
            'email': 'test14@test.com',
            'username': 'test3',
            'role_id': Role.query.filter_by(permission=0x11).first().id,
            'gender': 'Male',
            'degree': 'Bachelor',
            'country': 'China'
        }, follow_redirects=True)
        self.assertTrue(b'您无法编辑一个更高权限' in response.data)
        u2.role_id = Role.query.filter_by(permission=0x11).first().id
        db.session.add(u2)
        db.session.commit()
        response = self.client.post(url_for('admin.user_edit', user_id=u2.id), data={
            'email': 'test14@test.com',
            'username': 'test3',
            'role_id': Role.query.filter_by(permission=0xff).first().id,
            'gender': 'Male',
            'degree': 'Bachelor',
            'country': 'China'
        }, follow_redirects=True)
        self.assertTrue(b'您不能给用户授予高于您本身的权限' in response.data)
        response = self.client.post(url_for('admin.user_edit', user_id=u2.id), data={
            'email': 'test14@test.com',
            'username': 'test3',
            'role_id': Role.query.filter_by(permission=0x40).first().id,
            'gender': 'Male',
            'degree': 'Bachelor',
            'country': 'China'
        }, follow_redirects=True)
        self.assertTrue(b'您不能给用户授予高于您本身的权限' in response.data)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('admin.user_edit', user_id=u2.id), data={
            'email': 'test14@test.com',
            'username': 'test3',
            'role_id': Role.query.filter_by(permission=0xff).first().id,
            'gender': 'Male',
            'degree': 'Bachelor',
            'country': 'China'
        }, follow_redirects=True)
        self.assertFalse(b'您不能给用户授予高于您本身的权限' in response.data)
        self.assertFalse(b'您无法编辑一个更高权限' in response.data)
        u.role_id = Role.query.filter_by(permission=0x40).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('admin.user_edit', user_id=u.id), data={
            'email': 'test55@test.com',
            'username': 'test2',
            'role_id': Role.query.filter_by(permission=0x11).first().id,
            'gender': 'Male',
            'degree': 'Bachelor',
            'country': 'China'
        }, follow_redirects=True)
        self.assertFalse(b'您不能给用户授予高于您本身的权限' in response.data)
        self.assertFalse(b'您无法编辑一个更高权限' in response.data)

    def test_oj(self):

        '''
            test if admin oj part is good
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        response = self.client.post(url_for('admin.oj_status_insert'), data={
            'oj_name': 'oj_test',
            'url': 'http://127.0.0.1',
            'status': 0
        }, follow_redirects=True)
        self.assertTrue(b'Add oj status successful!' in response.data)
        response = self.client.get(url_for('admin.oj_list'))
        self.assertTrue(b'oj_test' in response.data)
        response = self.client.get(url_for('admin.oj_status', oj_id=1))
        self.assertTrue(b'oj_test' in response.data)
        response = self.client.get(url_for('admin.oj_status_edit', oj_id=1))
        self.assertTrue(b'oj_test' in response.data)
        response = self.client.post(url_for('admin.oj_status_edit', oj_id=1), data={
            'oj_name': 'oj_test2',
            'url': 'http://127.0.0.12',
            'status': 0
        }, follow_redirects=True)
        self.assertTrue(b'oj_test2' in response.data)
        self.assertTrue(b'http://127.0.0.12' in response.data)
        self.assertTrue(b'Update oj status successful!' in response.data)
        response = self.client.get(url_for('admin.oj_status_delete'), follow_redirects=True)
        self.assertTrue(b'No such oj in oj_list!' in response.data)
        response = self.client.get(url_for('admin.oj_status_delete', oj_id=2), follow_redirects=True)
        self.assertTrue(b'No such oj in oj_list!' in response.data)
        response = self.client.get(url_for('admin.oj_status_delete', oj_id=1), follow_redirects=True)
        self.assertTrue(b'Delete oj successful!' in response.data)
        response = self.client.get(url_for('admin.oj_list'))
        self.assertFalse(b'oj_test' in response.data)

    def test_submission(self):

        '''
            test status part
        :return: None
        '''

        u = User(username='test2', password='123456', email='test2@test.com', confirmed=True)
        u.role_id = Role.query.filter_by(permission=0xff).first().id
        db.session.add(u)
        db.session.commit()
        response = self.client.post(url_for('auth.login'), data={
            'username': 'test2',
            'password': '123456'
        }, follow_redirects=True)
        p = Problem(title='test', visible=True)
        db.session.add(p)
        db.session.commit()
        response = self.client.post(url_for('problem.submit', problem_id=p.id), data={
            'problem_id': p.id,
            'language': '1',
            'code': 'helloworldsdfsdf'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(b'G++' in response.data)
        self.client.get(url_for('admin.submission_status_list'))
        self.assertTrue(b'G++' in response.data)
        self.client.get(url_for('admin.submission_status_detail', submission_id=1))
        self.assertTrue(b'G++' in response.data)
        response = self.client.get(url_for('admin.submission_status_edit', submission_id=1))
        response = self.client.post(url_for('admin.submission_status_edit', submission_id=1), data={
            'status': '1',
            'exec_time': '1',
            'exec_memory': '1'
        }, follow_redirects=True)
        self.assertTrue(b'Accepted' in response.data)
