#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from app import create_app, db
import time
from datetime import datetime
from app.models import Topic, BlogComment, TopicComment, User, Contest, Blog

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

    def test_insert_topic(self):

        '''
            test to insert into a new topic and comment to database
        :return: None
        '''

        contest = Contest()
        db.session.add(contest)
        user = User(username='test')
        db.session.add(user)
        db.session.commit()
        topic = Topic()
        topic.contest_id = contest.id
        topic.author_username = user.username
        db.session.add(topic)
        db.session.commit()
        self.assertTrue(topic.contest.id == contest.id)
        comment = TopicComment()
        comment.topic_id = topic.id
        db.session.add(comment)
        db.session.commit()
        self.assertTrue(topic.comments.first().id == comment.id)
        db.session.delete(topic)
        db.session.commit()
        self.assertTrue(TopicComment.query.count() == 0)
        topic = Topic()
        topic.contest_id = contest.id
        topic.author_username = user.username
        db.session.add(topic)
        db.session.commit()
        comment = TopicComment()
        comment.topic_id = topic.id
        db.session.add(comment)
        db.session.commit()
        db.session.delete(contest)
        db.session.commit()
        self.assertTrue(Topic.query.count() == 0)

    def test_insert_blog(self):

        '''
            test to insert a blog into the database
        :return: None
        '''

        blog = Blog()
        db.session.add(blog)
        db.session.commit()
        comment = BlogComment()
        comment.blog_id = blog.id
        db.session.add(comment)
        db.session.commit()
        self.assertTrue(blog.comments.first().id == comment.id)
        db.session.delete(blog)
        db.session.commit()
        self.assertTrue(BlogComment.query.count() == 0)