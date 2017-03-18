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
import identicon, random, os

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
            role.permission = roles[r][0]
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
    operation = db.relationship('Logs', backref='operator', lazy='dynamic')
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
            code = random.randint(1, 1000000000000)
            icon = identicon.render_identicon(code, 48)
            icon.save('./app/static/photo/%08x.png' % code, 'PNG')
            self.photo = '%08x' % code

    def generate_auth_token(self, expiration=3600):

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

    @staticmethod
    def verify_auth_token(token):

        '''
            verify the token
        :param token: token
        :return: User info
        '''

        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    @property
    def password(self):

        '''
            raise error for setter
        :return: None
        '''

        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):

        '''
            generate password hash
        :param password: password
        :return: None
        '''

        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):

        '''
            check password vaild
        :param password: password
        :return: True or False
        '''

        return check_password_hash(self.password_hash, password)

    def generate_confirm_token(self, expiration=3600):

        '''
            generate confirm token for user register
        :param expiration: expiration time
        :return: token
        '''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_reset_token(self, expiration=3600):

        '''
            generate reset token for user reset password
        :param expiration: expiration time
        :return: token
        '''

        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):

        '''
            deal with reset password
        :param token: token
        :param new_password: new password
        :return: True or False
        '''

        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def confirm(self, token):

        '''
            confirm user register
        :param token: token
        :return: True or False
        '''

        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_email_change_token(self, new_email, expiration=3600):

        '''
            generate token for email change
        :param new_email: new email
        :param expiration: expiration time
        :return: token
        '''

        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):

        '''
            deal with operation change email
        :param token: token
        :return: True or False
        '''

        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True

    def change_photo_name(self):

        '''
            deal with operation change photo_name, two times hash with email
        :return: name
        '''

        self.photo = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.photo = self.photo + '.png'
        self.photo = hashlib.md5(self.photo.encode('utf-8')).hexdigest()
        return self.photo

    def can(self, permissions):

        '''
            judge if has permission
        :param permissions: permissions
        :return: True or False
        '''

        return self.role is not None and (self.role.permission & permissions) == permissions

    def is_admin(self):

        '''
            judge if is admin
        :return: True or False
        '''

        return self.can(Permission.ADMIN)

    def is_super_admin(self):

        '''
            judge if is super admin
        :return: True or False
        '''

        return self.can(Permission.SUPER_ADMIN)

    def ping(self):

        '''
            update user login time
        :return:
        '''

        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def follow(self, user):

        '''
            deal with follow operation
        :param user: the user current_user will follow
        :return: None
        '''

        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):

        '''
            deal with unfollow operation
        :param user: the user current_user will not follow
        :return: None
        '''

        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):

        '''
            judge if is following the user
        :param user: a user
        :return: True or False
        '''

        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):

        '''
            judge if current_user is followed by user
        :param user: a user
        :return: True or False
        '''

        return self.followers.filter_by(follower_id=user.id).first() is not None

    def log_operation(self, operations):

        '''
            deal with log operations
        :param operations: operations
        :return: None
        '''

        # Todo: need to test
        log = Logs(operator=self, operation=operations)
        db.session.add(log)
        db.session.commit()

    def __repr__(self):
        '''
            just a repr
        :return: string
        '''

        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):

    '''
        define AnonymousUser
    '''

    def can(self, permissions):
        '''
            permissions about AnonymousUser
        :param permissions: permissions
        :return: False
        '''

        return False

    def is_admin(self):
        '''
            judge if admin
        :return: False
        '''

        return self.can()

    def is_super_admin(self):
        '''
            judge if super admin
        :return: False
        '''

        return self.can()


class Logs(db.Model):

    '''
        define log table
    '''

    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    operator_name = db.Column(db.String(64), db.ForeignKey('users.username'))
    operation = db.Column(db.String(128))
    time = db.Column(db.DateTime(), default=datetime.utcnow)
