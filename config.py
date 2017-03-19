#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():

    '''
        config keys and values for whole app
    '''

    SECRET_KEY = os.environ.get("SECRET_KEY") or 'hard to guess string'

    # used for sending emails
    MAIL_SERVER = 'smtp.mxhichina.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'no_reply@myvjudge.cn'
    MAIL_PASSWORD = os.environ.get('MAIL_PASS')
    FLASKY_MAIL_SUBJECT_PREFIX = '[HEU Onlie Judge]'
    FLASKY_MAIL_SENDER = 'no_reply<no_reply@myvjudge.cn>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    # SERVER_NAME = 'myvjudge.cn'

    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    #SERVER_NAME = 'server_name'

    # about sql query and settings
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_STATUS_PER_PAGE = 50
    FLASKY_CONTESTS_PER_PAGE = 30
    UPLOADED_PATH = './data/'




    # used for submissions
    GLOBAL_SUBMISSION_STATUS = {
        'Waiting'               : 0,
        'Accepted'              : 1,
        'Compile Error'         : 2,
        'Wrong Answer'          : 3,
        'Presentation Error'    : 4,
        'Runtime Error'         : 5,
        'Time Limit Exceeded'   : 6,
        'Memory Limit Exceeded' : 7,
        'Output Limit Exceeded' : 8,
        'Restricted Function'   : 9,
        'Judging'               : 10,
        'Judge Error'           : 11
    }
    GLOBAL_LANGUAGE = {
        'GCC': 0,
        'G++': 1,
        'Java': 6,
        'Python2': 7,
        'Python3': 8,
    }


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    '''
        make config for development settings
    '''

    # debug setting
    Debug = True

    # sql database setting
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):

    '''
        make config for production settings
    '''

    if os.environ.get('MYSQL_ADDR'):
        SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s:%s/online_judge" % (os.environ.get('MYSQL_USER'), os.environ.get('MYSQL_PASS'), os.environ.get('MYSQL_ADDR'), os.environ.get('MYSQL_PORT'))
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('PRO_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


class TestConfig(Config):

    '''
        make config for test settings
    '''

    TESTING = True
    Debug = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

# config dicts for manage params
config = {
    'development': DevelopmentConfig,
    'production' : ProductionConfig,
    'testing'    : TestConfig,

    'default'    : DevelopmentConfig
}