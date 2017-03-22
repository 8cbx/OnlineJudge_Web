#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import create_app, db
from app.models import Permission, Role, User
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand



app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    '''
        make context to the shell
    :return: dicts
    '''
    return dict(app=app, db=db, Permission=Permission, Role=Role, User=User)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False):

    '''
        run the unit test
    :return: None
    '''

    # export coverage environment
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)


    import unittest

    # unit test
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.erase()

    return len(result.failures) or len(result.errors)


if __name__ == '__main__':
    '''
        run the judge web
    '''
    manager.run()
