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
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = os.environ.get('FLASKY_MAIL_SUBJECT_PREFIX')
    FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SERVER_NAME = os.environ.get('SERVER_NAME')
    SEND_EMAIL = False

    # about sql query and settings
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_FOLLOWERS_PER_PAGE = 50
    FLASKY_PROBLEMS_PER_PAGE = 50
    FLASKY_USERS_PER_PAGE = 50
    FLASKY_TAGS_PER_PAGE = 50
    FLASKY_STATUS_PER_PAGE = 50
    FLASKY_CONTESTS_PER_PAGE = 50
    FLASKY_OJS_PER_PAGE = 50
    FLASKY_LOGS_PER_PAGE = 50
    FLASKY_BLOGS_PER_PAGE = 50
    UPLOADED_PATH = './data/'

    # celery_settings
    '''
        celery_broker_url:
            sqlite: sqla+sqlite:///data.sqlite
            rabbitmq: amqp://guest:guest@192.168.1.1:5672
        celery_backend_url:
            sqlite: db+sqlite:///data.sqlite
            mysql: db+mysql://root:password@192.168.1.1:3306/celery_backend
    '''
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_BACKEND_URL')
    CELERY_ALWAYS_EAGER = False

    #sqlalchemy settings
    if os.environ.get('MYSQL_ADDR'):
        SQLALCHEMY_DATABASE_URI = "mysql://%s:%s@%s:%s/online_judge" % (os.environ.get('MYSQL_USER'), os.environ.get('MYSQL_PASS'), os.environ.get('MYSQL_ADDR'), os.environ.get('MYSQL_PORT'))
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('PRO_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

    # used for register
    COUNTRY = [("Andorra", "Andorra"), ("United Arab Emirates", "United Arab Emirates"), ("Afghanistan", "Afghanistan"), ("Antigua and Barbuda", "Antigua and Barbuda"), ("Anguilla", "Anguilla"), ("Albania", "Albania"), ("Armenia", "Armenia"), ("Angola", "Angola"), ("Argentina", "Argentina"), ("Austria", "Austria"),("Australia", "Australia"), ("Azerbaijan", "Azerbaijan"), ("Barbados", "Barbados"), ("Bangladesh", "Bangladesh"), ("Belgium", "Belgium"), ("Burkina-faso", "Burkina-faso"), ("Bulgaria", "Bulgaria"), ("Bahrain", "Bahrain"), ("Burundi", "Burundi"), ("Benin", "Benin"), ("Palestine", "Palestine"), ("Bermuda Is.", "Bermuda Is."), ("Brunei", "Brunei"), ("Bolivia", "Bolivia"), ("Brazil", "Brazil"), ("Bahamas", "Bahamas"), ("Botswana", "Botswana"), ("Belarus", "Belarus"), ("Belize", "Belize"), ("Canada", "Canada"), ("Central African Republic", "Central African Republic"), ("Congo", "Congo"), ("Switzerland", "Switzerland"), ("Cook Is.", "Cook Is."), ("Chile", "Chile"), ("Cameroon", "Cameroon"), ("China", "China"), ("Colombia", "Colombia"), ("Costa Rica", "Costa Rica"), ("Czech", "Czech"), ("Cuba", "Cuba"), ("Cyprus", "Cyprus"), ("Czech Republic", "Czech Republic"), ("Germany", "Germany"), ("Djibouti", "Djibouti"), ("Denmark", "Denmark"), ("Dominica Rep.", "Dominica Rep."), ("Algeria", "Algeria"), ("Ecuador", "Ecuador"), ("Estonia", "Estonia"), ("Egypt", "Egypt"), ("Spain", "Spain"), ("Ethiopia", "Ethiopia"), ("Finland", "Finland"), ("Fiji", "Fiji"), ("France", "France"), ("Gabon", "Gabon"), ("United Kiongdom", "United Kiongdom"), ("Grenada", "Grenada"), ("Georgia", "Georgia"), ("French Guiana", "French Guiana"), ("Ghana", "Ghana"), ("Gibraltar", "Gibraltar"), ("Gambia", "Gambia"), ("Guinea", "Guinea"), ("Greece", "Greece"), ("Guatemala", "Guatemala"), ("Guam", "Guam"), ("Guyana", "Guyana"), ("Hongkong", "Hongkong"), ("Honduras", "Honduras"), ("Haiti", "Haiti"), ("Hungary", "Hungary"), ("Indonesia", "Indonesia"), ("Ireland", "Ireland"), ("Israel", "Israel"), ("India", "India"), ("Iraq", "Iraq"), ("Iran", "Iran"), ("Iceland", "Iceland"), ("Italy", "Italy"), ("Jamaica", "Jamaica"), ("Jordan", "Jordan"), ("Japan", "Japan"), ("Kenya", "Kenya"), ("Kyrgyzstan", "Kyrgyzstan"), ("Kampuchea (Cambodia)", "Kampuchea (Cambodia)"), ("North Korea", "North Korea"), ("Korea", "Korea"), ("Republic of Ivory Coast", "Republic of Ivory Coast"), ("Kuwait", "Kuwait"), ("Kazakstan", "Kazakstan"), ("Laos", "Laos"), ("Lebanon", "Lebanon"), ("St.Lucia", "St.Lucia"), ("Liechtenstein", "Liechtenstein"), ("Sri Lanka", "Sri Lanka"), ("Liberia", "Liberia"), ("Lesotho", "Lesotho"), ("Lithuania", "Lithuania"), ("Luxembourg", "Luxembourg"), ("Latvia", "Latvia"), ("Libya", "Libya"), ("Morocco", "Morocco"), ("Monaco", "Monaco"), ("The Republic of Moldova", "The Republic of Moldova"), ("Madagascar", "Madagascar"), ("Mali", "Mali"), ("Burma", "Burma"), ("Mongolia", "Mongolia"), ("Macao", "Macao"), ("Montserrat Is", "Montserrat Is"), ("Malta", "Malta"), ("Mauritius", "Mauritius"), ("Maldives", "Maldives"), ("Malawi", "Malawi"), ("Mexico", "Mexico"), ("Malaysia", "Malaysia"), ("Mozambique", "Mozambique"), ("Namibia", "Namibia"), ("Niger", "Niger"), ("Nigeria", "Nigeria"), ("Nicaragua", "Nicaragua"), ("Netherlands", "Netherlands"), ("Norway", "Norway"), ("Nepal", "Nepal"), ("Nauru", "Nauru"), ("New Zealand", "New Zealand"), ("Oman", "Oman"), ("Panama", "Panama"), ("Peru", "Peru"), ("French Polynesia", "French Polynesia"), ("Papua New Cuinea", "Papua New Cuinea"), ("Philippines", "Philippines"), ("Pakistan", "Pakistan"), ("Poland", "Poland"), ("Puerto Rico", "Puerto Rico"), ("Portugal", "Portugal"), ("Paraguay", "Paraguay"), ("Qatar", "Qatar"), ("Romania", "Romania"), ("Russia", "Russia"), ("Saudi Arabia", "Saudi Arabia"), ("Solomon Is", "Solomon Is"), ("Seychelles", "Seychelles"), ("Sudan", "Sudan"), ("Sweden", "Sweden"), ("Singapore", "Singapore"), ("Slovenia", "Slovenia"), ("Slovakia", "Slovakia"), ("Sierra Leone", "Sierra Leone"), ("San Marino", "San Marino"), ("Senegal", "Senegal"), ("Somali", "Somali"), ("Suriname", "Suriname"), ("Sao Tome and Principe", "Sao Tome and Principe"), ("EI Salvador", "EI Salvador"), ("Syria", "Syria"), ("Swaziland", "Swaziland"), ("Chad", "Chad"), ("Togo", "Togo"), ("Thailand", "Thailand"), ("Tajikstan", "Tajikstan"), ("Turkmenistan", "Turkmenistan"), ("Tunisia", "Tunisia"), ("Tonga", "Tonga"), ("Turkey", "Turkey"), ("Trinidad and Tobago", "Trinidad and Tobago"), ("Taiwan", "Taiwan"), ("Tanzania", "Tanzania"), ("Ukraine", "Ukraine"), ("Uganda", "Uganda"), ("United States of America", "United States of America"), ("Uruguay", "Uruguay"), ("Uzbekistan", "Uzbekistan"), ("Saint Vincent", "Saint Vincent"), ("Venezuela", "Venezuela"), ("Vietnam", "Vietnam"), ("Yemen", "Yemen"), ("Yugoslavia", "Yugoslavia"), ("South Africa", "South Africa"), ("Zambia", "Zambia"), ("Zaire", "Zaire")]
    GENDER = [("Male", "Male"), ("Female", "Female")]
    DEGREE = [("Bachelor", "Bachelor"), ("Master", "Master"), ("Doctor", "Doctor"), ("Junior College", "Junior College"), ("High School", "High School"), ("Middle School", "Middle School"), ("Working", "Working")]

    # used for submissions
    LOCAL_SUBMISSION_STATUS = {
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
    LOCAL_LANGUAGE = {
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