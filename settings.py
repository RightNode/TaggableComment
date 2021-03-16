#!/usr/bin/env python3
# -*- coding: utf-8 -*-
class BaseConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:mysql@localhost:3306/graduation_project"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = "graduation_project"


class DevelopmentConfig(BaseConfig):
    ENV = "development"


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"


class TestConfig(BaseConfig):
    DEBUG = False
    ENV = "testing"
