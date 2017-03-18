#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import Permission, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
import os


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    '''
        make context to the shell
    :return: dicts
    '''
    return dict(app=app, db=db, Permission=Permission, Role=Role)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():

    '''
        run the unit test
    :return: None
    '''

    import unittest
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    return len(result.failures)


if __name__ == '__main__':
    '''
        run the judge web
    '''
    manager.run()
