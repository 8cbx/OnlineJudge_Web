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


class ContestUsers(db.Model):

    '''
        define contest with user relationship
    '''

    __tablename__ = 'contest_user'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), primary_key=True)
    realname = db.Column(db.String(32))
    address = db.Column(db.String(128))
    school = db.Column(db.String(128))
    student_num = db.Column(db.String(64))
    phone_num = db.Column(db.String(32))
    user_confirmed = db.Column(db.Boolean, default=False)
    register_time = db.Column(db.DateTime, default=datetime.utcnow)


class ContestProblem(db.Model):

    '''
        define contest with problem relationship
    '''

    __tablename__ = 'contest_problem'
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), primary_key=True)
    problem_index = db.Column(db.Integer)
    problem_alias = db.Column(db.String(64))


class TagProblem(db.Model):

    '''
        define Tag with problem relationship
    '''

    __tablename__ = 'tag_problem'
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), primary_key=True)


class User(UserMixin, db.Model):

    '''
        define user, include user info, and operations
    '''

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    nickname = db.Column(db.String(64))
    realname = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    gender = db.Column(db.String(64))
    major = db.Column(db.String(64))
    degree = db.Column(db.String(64))
    country = db.Column(db.String(128))
    address = db.Column(db.String(128))
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
    submission = db.relationship('SubmissionStatus', backref='auther', lazy='dynamic', cascade='all, delete-orphan')
    manage_contest = db.relationship('Contest', backref='manager', lazy='dynamic', cascade='all, delete-orphan')
    operation = db.relationship('Logs', backref='operator', lazy='dynamic', cascade='all, delete-orphan')
    blog_comments = db.relationship('BlogComment', backref='author', lazy='dynamic')
    topic_comments = db.relationship('TopicComment', backref='author', lazy='dynamic')
    contest = db.relationship(
        'ContestUsers',
        foreign_keys=[ContestUsers.user_id],
        backref=db.backref('user', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
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
            icon = identicon.render_identicon(code, 128)
            icon.save('./app/static/photo/%08x.png' % code, 'PNG')
            self.photo = '%08x' % code
        if self.nickname is None:
            self.nickname = self.username

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

        return self.can(Permission.ADMIN)

    def is_super_admin(self):
        '''
            judge if super admin
        :return: False
        '''

        return self.can(Permission.SUPER_ADMIN)


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):

    '''
        load user
    :param user_id: user id
    :return: user
    '''

    return User.query.get(int(user_id))


class OJList(db.Model):

    '''
        define OJ list, and some of the operations
    '''

    __tablename__ = 'oj_list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    url = db.Column(db.String(128))
    vjudge = db.Column(db.Boolean, default=False)
    status = db.Column(db.Integer)
    problems = db.relationship('Problem', backref='oj', lazy='dynamic', cascade='all, delete-orphan')
    last_check = db.Column(db.DateTime(), default=datetime.utcnow)

    def ping(self):

        '''
            update last_check value
        :return: None
        '''

        self.last_check = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def to_json(self):

        '''
            oj status to json
        :return: json
        '''

        json_oj_list = {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'last_check': self.last_check
        }
        return json_oj_list


class Problem(db.Model):

    '''
        define problem, and some operation about problem
    '''

    __tablename__ = 'problems'
    # local id for problem
    id = db.Column(db.Integer, primary_key=True)
    # remote id for problem
    remote_id = db.Column(db.Integer, index=True)
    oj_id = db.Column(db.Integer, db.ForeignKey("oj_list.id"))
    title = db.Column(db.String(128), index=True)
    time_limit = db.Column(db.Integer)
    memory_limit = db.Column(db.Integer)
    special_judge = db.Column(db.Boolean, default=False)
    # False for ACM, True for OI
    type = db.Column(db.Boolean, default=False)
    submission_num = db.Column(db.Integer)
    accept_num = db.Column(db.Integer)
    description = db.Column(db.Text)
    input = db.Column(db.Text)
    output = db.Column(db.Text)
    sample_input = db.Column(db.Text)
    sample_output = db.Column(db.Text)
    source_name = db.Column(db.String(128))
    hint = db.Column(db.Text)
    author = db.Column(db.String(128))
    last_update = db.Column(db.DateTime(), default=datetime.utcnow)
    visible = db.Column(db.Boolean, default=False)
    submissions = db.relationship('SubmissionStatus', backref='problem', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship(
        'TagProblem',
        foreign_keys=[TagProblem.problem_id],
        backref=db.backref('problem', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    contest = db.relationship(
        'ContestProblem',
        foreign_keys=[ContestProblem.problem_id],
        backref=db.backref('problem', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):

        '''
            init class, generate user role and photo
        :param kwargs: kwargs
        '''

        super(Problem, self).__init__(**kwargs)
        if self.submission_num is None:
            self.submission_num = 0
        if self.accept_num is None:
            self.accept_num = 0

    def to_json(self):

        '''
            problem to json
        :return: json
        '''

        json_problem = {
            'id': self.id,
            'remomte_id': self.remote_id,
            'oj_id': self.oj_id,
            'title': self.title
        }
        return json_problem

    @staticmethod
    def from_json(json_problem):

        '''
            update problem item using json
        :param json_problem: json
        :return: problem item
        '''

        oj_id = json_problem.get('oj_id')
        remote_id = json_problem.get('remote_id')
        title = json_problem.get('title')
        time_limit = json_problem.get('time_limit')
        memory_limit = json_problem.get('memory_limit')
        special_judge = json_problem.get('special_judge')
        submission_num = json_problem.get('submission_num')
        accept_num = json_problem.get('accept_num')
        description = json_problem.get('description')
        input = json_problem.get('input')
        output = json_problem.get('output')
        sample_input = json_problem.get('sample_input')
        sample_output = json_problem.get('sample_output')
        source_name = json_problem.get('source_name')
        hint = json_problem.get('hint')
        author = json_problem.get('author')
        last_update = datetime.utcnow()
        if title is None or title == '' or description is None or description == '' or oj_id is None or oj_id == '' or remote_id == '' or remote_id is None:
            raise ValidationError('Problem require full data')
        return Problem(oj_id=oj_id, remote_id=remote_id, title=title, time_limit=time_limit, memory_limit=memory_limit, special_judge=special_judge, submission_num=submission_num, accept_num=accept_num, description=description, input=input, output=output, sample_input=sample_input, sample_output=sample_output, source_name=source_name, hint=hint, author=author, last_update=last_update)


class SubmissionStatus(db.Model):

    '''
        define Submissions and status with some operation
    '''

    __tablename__ = 'submission_status'
    id = db.Column(db.Integer, primary_key=True)
    submit_time = db.Column(db.DateTime(), default=datetime.utcnow)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'))
    status = db.Column(db.Integer, index=True)
    exec_time = db.Column(db.Integer)
    exec_memory = db.Column(db.Integer)
    code_length = db.Column(db.Integer)
    language = db.Column(db.Integer)
    code = db.Column(db.Text)
    author_username = db.Column(db.String(64), db.ForeignKey('users.username'))
    visible = db.Column(db.Boolean, default=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'))
    balloon_sent = db.Column(db.Boolean, default=False)
    submit_ip = db.Column(db.String(32))

    def send_balloon(self):

        '''
            deal with sent balloon operation
        :return: None
        '''

        self.balloon_sent = True
        db.session.add(self)
        db.session.commit()

    def to_json(self):

        '''
            submissions to json
        :return: json
        '''

        json_submission={
            'id': self.id,
            'submit_time': self.submit_time,
            'problem_id': self.problem_id,
            'language': self.language,
            'status': self.status,
            'code': self.code,
            'max_time': self.problem.time_limit,
            'max_memory': self.problem.memory_limit,
            'special_judge': 1 if self.problem.special_judge is True else 0,
            'problem_type': 1 if self.problem.type is True else 0,
            'vjudge': 1 if self.problem.oj.first().vjudge is True else 0,
            'oj': self.problem.oj.first().name
        }
        return json_submission

    @staticmethod
    def from_json(json_submission):

        '''
            update submissions using json
        :param json_submission:
        :return: submission item
        '''

        status = json_submission.get('status')
        exec_time = json_submission.get('exec_time')
        exec_memory = json_submission.get('exec_memory')
        if status is None or status == '' or exec_time is None or exec_time == '' or exec_memory is None or exec_memory == '':
            raise ValidationError('Status require full data')
        return SubmissionStatus(status=status, exec_time=exec_time, exec_memory=exec_memory)


class CompileInfo(db.Model):

    '''
        define compile info and some operations
    '''

    __tablename__ = 'compile_info'
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission_status.id'))
    info = db.Column(db.Text)

    def to_json(self):

        '''
            compile info to json
        :return: json
        '''

        json_compile_info = {
            'id': self.id,
            'submission_id': self.submission_id,
            'info': self.info
        }
        return json_compile_info

    @staticmethod
    def from_json(json_compile_info):

        '''
            update compile info using json
        :param json_compile_info: json
        :return: compile_info item
        '''

        info = json_compile_info.get('info')
        if info is None or info == '':
            raise ValidationError('Compile_info require full data')
        return CompileInfo(info=info)


class Contest(db.Model):

    '''
        define contest table and some operations
    '''

    __tablename__ = 'contests'
    id = db.Column(db.Integer, primary_key=True)
    contest_name = db.Column(db.String(128), index=True)
    start_time = db.Column(db.DateTime(), default=datetime.utcnow)
    end_time = db.Column(db.DateTime(), default=datetime.utcnow)
    # need to verify by the manager
    verify = db.Column(db.Boolean)
    # password type of the contest
    password = db.Column(db.String(64))
    # define what type is the contest
    style = db.Column(db.Integer)
    # description of the contest, show in the first page, or the register page
    description = db.Column(db.Text)
    # announcement of the problem page
    announce = db.Column(db.Text)
    # notification in the problem page, status page, rank page
    notification = db.Column(db.Text)
    manager_username = db.Column(db.String(64), db.ForeignKey('users.username'))
    visible = db.Column(db.Boolean, default=True)
    rank_frozen = db.Column(db.Boolean, default=True)
    last_generate_rank = db.Column(db.DateTime(), default=datetime.utcnow)
    problems = db.relationship(
        'ContestProblem',
        foreign_keys=[ContestProblem.contest_id],
        backref=db.backref('contest', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    submissions = db.relationship('SubmissionStatus', backref='contest', lazy='dynamic', cascade='all, delete-orphan')
    topics = db.relationship('Topic', backref='contest', lazy='dynamic', cascade='all, delete-orphan')
    users = db.relationship(
        'ContestUsers',
        foreign_keys=[ContestUsers.contest_id],
        backref=db.backref('contest', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )


class Tag(db.Model):

    '''
        define tag table
    '''

    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(32), unique=True)
    problems = db.relationship(
        'TagProblem',
        foreign_keys=[TagProblem.tag_id],
        backref=db.backref('tag', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )


class Logs(db.Model):

    '''
        define log table
    '''

    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    operator_name = db.Column(db.String(64), db.ForeignKey('users.username'))
    operation = db.Column(db.String(128))
    time = db.Column(db.DateTime(), default=datetime.utcnow)


class Topic(db.Model):

    '''
        define topic in contest table
    '''

    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    content = db.Column(db.Text)
    author_username = db.Column(db.String(64), db.ForeignKey('users.username'))
    public = db.Column(db.Boolean())
    last_update = db.Column(db.DateTime(), default=datetime.utcnow)

    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'))
    comments = db.relationship('TopicComment', backref='topic', lazy='dynamic', cascade='all, delete-orphan')


class Blog(db.Model):

    '''
        define blog table
    '''

    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    content = db.Column(db.Text)
    author_username = db.Column(db.String(64), db.ForeignKey('users.username'))
    public = db.Column(db.Boolean(), default=False)
    last_update = db.Column(db.DateTime(), default=datetime.utcnow)
    comments = db.relationship('BlogComment', backref='blog', lazy='dynamic', cascade='all, delete-orphan')


class TopicComment(db.Model):

    '''
        define topic comment
    '''

    __tablename__ = 'topic_comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text())
    author_username = db.Column(db.String(64), db.ForeignKey('users.username'))
    time = db.Column(db.DateTime(), default=datetime.utcnow)
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"))

class BlogComment(db.Model):

    '''
        define blog comment
    '''

    __tablename__ = 'blog_comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text())
    author_username = db.Column(db.String(64), db.ForeignKey('users.username'))
    time = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    blog_id = db.Column(db.Integer, db.ForeignKey("blog.id"))