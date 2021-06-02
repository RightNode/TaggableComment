# coding: utf-8
from exts import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)


class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True)
    # content = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)

    user = db.relationship('User', primaryjoin='Article.user_id == User.id', backref='articles')


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(20), nullable=False, unique=True)

    def __init__(self, tag_name):
        self.tag_name = tag_name


class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    thumb_up = db.Column(db.Integer, server_default=db.FetchedValue())
    thumb_down = db.Column(db.Integer, server_default=db.FetchedValue())
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    article_id = db.Column(db.ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    parent_id = db.Column(db.ForeignKey('comment.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)

    # Article对象可以通过comments属性来获取相应的Comment对象列表
    article = db.relationship('Article', primaryjoin='Comment.article_id == Article.id', backref='comments')
    # parent = db.relationship('Comment', remote_side=[id], primaryjoin='Comment.parent_id == Comment.id',
    #                          backref=db.backref('replies', order_by=-created_at))
    parent = db.relationship('Comment', remote_side=[id], primaryjoin='Comment.parent_id == Comment.id', backref='replies')
    user = db.relationship('User', primaryjoin='Comment.user_id == User.id', backref='comments')

    def __init__(self, content, article_id=None, user_id=None, parent_id=None, article=None, parent=None, user=None):
        self.content = content

        if article_id is not None and article is None:
            self.article_id = article_id
        elif article_id is None and article is not None:
            self.article = article

        if user_id is not None and user is None:
            self.user_id = user_id
        elif user_id is None and user is not None:
            self.user = user

        if parent_id is not None and parent is None:
            self.parent_id = parent_id
        elif parent_id is None and parent is not None:
            self.parent = parent


class UserFilterTag(db.Model):
    __tablename__ = 'user_filter_tag'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False, unique=True)
    tag_ids = db.Column(db.String(200), nullable=False)

    user = db.relationship('User', primaryjoin='UserFilterTag.user_id == User.id', backref='user_filter_tags')

    def __init__(self, user_id, id_list):
        self.user_id = user_id
        self.tag_ids = ",".join([str(a) for a in sorted(set(id_list))])

    def get_id_list(self):
        return [int(a) for a in self.tag_ids.split(",")]


class CommentTag(db.Model):
    __tablename__ = 'comment_tag'

    id = db.Column(db.Integer, primary_key=True)
    cmt_id = db.Column(db.ForeignKey('comment.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    tag_id = db.Column(db.ForeignKey('tag.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    article_id = db.Column(db.ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    num = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())

    article = db.relationship('Article', primaryjoin='CommentTag.article_id == Article.id', backref='comment_tags')
    cmt = db.relationship('Comment', primaryjoin='CommentTag.cmt_id == Comment.id', backref='comment_tags')
    tag = db.relationship('Tag', primaryjoin='CommentTag.tag_id == Tag.id', backref='comment_tags')

    def __init__(self, cmt_id=None, tag_id=None, article_id=None, cmt=None, tag=None, article=None):
        if cmt_id is not None and cmt is None:
            self.cmt_id = cmt_id
        elif cmt_id is None and cmt is not None:
            self.cmt = cmt

        if tag_id is not None and tag is None:
            self.tag_id = tag_id
        elif tag_id is None and tag is not None:
            self.tag = tag

        if article_id is not None and article is None:
            self.article_id = article_id
        elif article_id is None and article is not None:
            self.article = article


class UserCmtTag(db.Model):
    __tablename__ = 'user_cmt_tag'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    cmt_id = db.Column(db.ForeignKey('comment.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    tag_id = db.Column(db.ForeignKey('tag.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    article_id = db.Column(db.ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    article = db.relationship('Article', primaryjoin='UserCmtTag.article_id == Article.id', backref='user_cmt_tags')
    cmt = db.relationship('Comment', primaryjoin='UserCmtTag.cmt_id == Comment.id', backref='user_cmt_tags')
    tag = db.relationship('Tag', primaryjoin='UserCmtTag.tag_id == Tag.id', backref='user_cmt_tags')
    user = db.relationship('User', primaryjoin='UserCmtTag.user_id == User.id', backref='user_cmt_tags')

    def __init__(self, user_id=None, cmt_id=None, tag_id=None, article_id=None, cmt=None, tag=None, user=None, article=None):
        if user_id is not None and user is None:
            self.user_id = user_id
        elif user_id is None and user is not None:
            self.user = user

        if cmt_id is not None and cmt is None:
            self.cmt_id = cmt_id
        elif cmt_id is None and cmt is not None:
            self.cmt = cmt

        if tag_id is not None and tag is None:
            self.tag_id = tag_id
        elif tag_id is None and tag is not None:
            self.tag = tag

        if article_id is not None and article is None:
            self.article_id = article_id
        elif article_id is None and article is not None:
            self.article = article
