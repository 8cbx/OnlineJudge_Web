#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time
from datetime import datetime
from app.models import CompileInfo, SubmissionStatus

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

    def test_compileinfo_add_new(self):

        '''
            test to insert into a new compile info to database
        :return: None
        '''

        status = SubmissionStatus()
        db.session.add(status)
        db.session.commit()
        info = CompileInfo(info='test', submission_id=status.id)
        db.session.add(info)
        db.session.commit()
        self.assertTrue(CompileInfo.query.count() == 1)


    def test_to_json(self):

        '''
            test for to_json func is good
        :return: None
        '''

        status = SubmissionStatus()
        db.session.add(status)
        db.session.commit()
        info = CompileInfo(info='test', submission_id=status.id)
        db.session.add(info)
        db.session.commit()
        info_json = info.to_json()
        self.assertTrue(info_json['id'] == 1)

    def test_from_json(self):

        '''
            test for from_json func is good
        :return: None
        '''

        info_dict = {
            'submission_id': 1,
            'info': 'test'
        }
        info = CompileInfo.from_json(info_dict)
        db.session.add(info)
        db.session.commit()
        self.assertTrue(info.id == 1)

    def test_compileinfo_with_status_delete(self):

        '''
            test for if the status delete, compile_info does not delete together
        :return: None
        '''

        status = SubmissionStatus()
        db.session.add(status)
        db.session.commit()
        info = CompileInfo(info='test', submission_id=status.id)
        db.session.add(info)
        db.session.commit()
        self.assertTrue(info.submission_id == status.id)
        db.session.delete(status)
        db.session.commit()
        self.assertTrue(CompileInfo.query.count() == 1)

