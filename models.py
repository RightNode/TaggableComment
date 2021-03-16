# coding: utf-8
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(10), nullable=False)
    uid = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)

    user = db.relationship('User', primaryjoin='Article.uid == User.id', backref='articles')



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

    article = db.relationship('Article', primaryjoin='Comment.article_id == Article.id', backref='comments')
    parent = db.relationship('Comment', remote_side=[id], primaryjoin='Comment.parent_id == Comment.id', backref='comments')
    user = db.relationship('User', primaryjoin='Comment.user_id == User.id', backref='comments')



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



class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(20), nullable=False, unique=True)



class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)



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
