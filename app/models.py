#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from app.exceptions import ValidationError
import identicorn, random, os

class Permission(object):

    '''
        settings about Permissions, using Hex expression
    '''

    SUBMIT_CODE     = 0x01
    EDIT_TAG        = 0x02
    WATCH_CODE      = 0x04
    MODIFY_PROBLEM  = 0x08
    MODIFY_CONTEST  = 0x10
    JUDGER          = 0x20
    ADMIN           = 0x40
    SUPER_ADMIN     = 0x80

    def __init__(self):

        pass


class KeyValue(db.Model):

    '''
        define Key-Value database for this judge
    '''

    __tablename__ = 'config'
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text)


class Role(db.Model):

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permission = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():

        '''
            insert roles to role table
        :return: None
        '''

        # init roles
        roles = {
            'User' : (Permission.SUBMIT_CODE | Permission.MODIFY_CONTEST, True),
            'Local Judger' : (Permission.JUDGER, False),
            'Remote Judger': (Permission.JUDGER, False),
            'Administrator': (Permission.ADMIN, False),
            "Super Administrator": (0xff, False)
        }

        # query and insert roles
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):

    '''
        define follow relationship
    '''

    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):

    '''
        define user, include user info, and operations
    '''

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    nickname = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    gender = db.Column(db.String(64))
    major = db.Column(db.String(64))
    degree = db.Column(db.String(64))
    country = db.Column(db.String(128))
    school = db.Column(db.String(128))
    student_num = db.Column(db.String(64))
    phone_num = db.Column(db.String(32))
    about_me = db.Column(db.Text)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    rating = db.Column(db.Integer, default=1500)
    photo = db.Column(db.String(64))
    # Todo: need to update to all connection part
    info_protection = db.Column(db.Boolean, default=False)
    #submission = db.relationship('SubmissionStatus', backref='auther', lazy='dynamic')
    #manage_contest = db.relationship('Contest', backref='manager', lazy='dynamic')
    #operation = db.relationship('Logs', backref='operator', lazy='dynamic')
    followed = db.relationship(
        'Follow',
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    followers = db.relationship(
        'Follow',
        foreign_keys=[Follow.followed_id],
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):

        '''
            init class, generate user role and photo
        :param kwargs: kwargs
        '''

        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permission=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.photo is None:
            code = 2147483068 + random.randint(1, 1000000000000)
            icon = identicorn.render_identicon(code, 48)
            icon.save('./app/static/photo/%08x.png' % code, 'PNG')
            self.photo = '%08x' % code

    def generate_auth_token(self, expiration):

        '''
            generate the auth token
        :param expiration: expiration time
        :return: token
        '''

        s = Serializer(
            current_app.config['SECRET_KEY'],
            expires_in=expiration
        )
        return s.dumps({'id': self.id})
