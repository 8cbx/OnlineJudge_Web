#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint

problem = Blueprint('problem', __name__)

from . import views

