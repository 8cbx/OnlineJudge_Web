#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import logging, os
from logging.handlers import RotatingFileHandler

# init moment obj and db obj
moment = Moment()
db = SQLAlchemy()

# set login params, user basic protection and set the view of login page
login_manager = LoginManager()
login_manager.session_protection = 'basic'
login_manager.login_view = 'auth.login'

# create flask app
def create_app(config_name):

    '''
        create app with config
    :param config_name: config settings
    :return: app
    '''

    # use config init app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # config moment, db, loginManager with app
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # register url for different part
    # index part
    from .index import index as index_blueprint
    app.register_blueprint(index_blueprint)
    # login and register part
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    # admin part
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    # contest part
    from .contest import contest as contest_blueprint
    app.register_blueprint(contest_blueprint, url_prefix='/contest')
    # api v1.0 part
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    # config logger part if not set debug flag
    if not app.debug:
        if os.environ.get("HOSTNAME"):
            pre_fix=os.environ.get("HOSTNAME")
        else:
            pre_fix=''
        file_handler = RotatingFileHandler('./judge-%s.log' % pre_fix, 'a', 1*1024*1024, 10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s: %(lineno)d]'))
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('Judge Contest StartUp')

    return app