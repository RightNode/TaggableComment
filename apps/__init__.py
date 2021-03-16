#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask

import settings
from apps.comment.views import cmt_bp
from exts import db


def create_app():
    # 创建app
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    # 加载配置
    app.config.from_object(settings.DevelopmentConfig)
    # 关联数据库
    db.init_app(app)
    # 在app中注册蓝图
    app.register_blueprint(cmt_bp)

    return app
