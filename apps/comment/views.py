#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from flask_cors import cross_origin
from sqlalchemy import desc, and_, asc

from apps.comment.models import Comment, Tag, UserCmtTag, CommentTag
from exts import db

cmt_bp = Blueprint("comment", __name__)


@cmt_bp.before_request
def set_before():
    session["article_id"] = 1
    session["user_id"] = 1
    session["username"] = "Admin"
    session["thumb_up_id"] = Tag.query.filter_by(tag_name="thumb_up").first().id
    session["thumb_down_id"] = Tag.query.filter_by(tag_name="thumb_down").first().id


@cmt_bp.route("/", methods=["POST", "GET"])
def cmts_page():
    # 获取用户名、用户ID和文章ID
    username = session["username"]
    user_id = session["user_id"]
    article_id = session["article_id"]
    up_id = session["thumb_up_id"]
    down_id = session["thumb_down_id"]

    # 获取当前用户在该文章中对所有评论所做的操作，这些记录会用于主页初始化时的图标标注
    user_tu_rec = []  # 保存的是用户在该篇文章中的点赞记录，值为comment.id的list
    user_td_rec = []  # 保存的是用户在该篇文章中的点踩记录，值为comment.id的list
    user_tag_rec = []  # 保存的是用户在该篇文章中，所有评论里的标签记录，每条记录由(comment.id, tag.id)这样的元组组成
    for uct in UserCmtTag.query.filter_by(user_id=user_id, article_id=article_id).all():
        if uct.tag_id == up_id:
            user_tu_rec.append(uct.cmt_id)
        elif uct.tag_id == down_id:
            user_td_rec.append(uct.cmt_id)
        else:
            user_tag_rec.append((uct.cmt_id, uct.tag_id))

    all_tags_in_atl = {cmt_tag.tag for cmt_tag in CommentTag.query.filter_by(article_id=session["article_id"]).all() if cmt_tag.cmt.parent_id is None}

    if request.method == "GET":
        sorted_by = "time-desc"
        filter_tag_ids = None
        cmts = Comment.query.filter(and_(Comment.parent_id.is_(None), Comment.article_id == article_id)).order_by(desc(Comment.created_at)).all()
    else:  # for POST
        sorted_by = request.form.get("sorted_by")
        filter_tag_ids = [int(id) for id in request.form.getlist("filter_tag_ids[]")]

        temp_cmts = None
        if sorted_by == "time-desc":
            temp_cmts = Comment.query.filter(and_(Comment.parent_id.is_(None), Comment.article_id == article_id)).order_by(
                desc(Comment.created_at)).all()
        if sorted_by == "time-asc":
            temp_cmts = Comment.query.filter(and_(Comment.parent_id.is_(None), Comment.article_id == article_id)).order_by(
                asc(Comment.created_at)).all()
        if sorted_by == "thumb-up":
            temp_cmts = Comment.query.filter(and_(Comment.parent_id.is_(None), Comment.article_id == article_id)).order_by(desc(Comment.thumb_up),
                                                                                                                           desc(
                                                                                                                               Comment.created_at)).all()
        if sorted_by == "thumb-down":
            temp_cmts = Comment.query.filter(and_(Comment.parent_id.is_(None), Comment.article_id == article_id)).order_by(desc(Comment.thumb_down),
                                                                                                                           desc(
                                                                                                                               Comment.created_at)).all()

        cmts = []
        if filter_tag_ids is not None:
            for cmt in temp_cmts:
                flag = True
                for cmt_tag in cmt.comment_tags:
                    if cmt_tag.tag_id in filter_tag_ids:
                        flag = False
                        break
                if flag:
                    cmts.append(cmt)
        else:
            cmts = temp_cmts

    return render_template("comment/comment.html", username=username, user_id=user_id, cmts=cmts, user_tu_rec=user_tu_rec, user_td_rec=user_td_rec,
                           user_tag_rec=user_tag_rec, all_tags_in_atl=all_tags_in_atl, sorted_by=sorted_by, filter_tag_ids=filter_tag_ids)


@cmt_bp.route("/new_comment", methods=["POST"])
def new_comment():
    content = request.form.get("cmt_content")
    if content is not None:
        content = content.strip()
        if content != "":
            parent_id = request.form.get("cmt_parent_id")
            user_id = session["user_id"]
            article_id = session["article_id"]

            if parent_id == "":
                parent_id = None

            cmt = Comment(content=content, parent_id=parent_id, user_id=user_id, article_id=article_id)
            db.session.add(cmt)
            # TODO: 这里还差一个给评论自动生成标签的过程
            # 直接调用函数或有问题，或许只能直接写成if判断
            db.session.commit()

    return redirect(url_for("comment.index"))


@cmt_bp.route("/thumb_up_action", methods=["POST"])
@cross_origin()
def thumb_up_action():
    """
    整体逻辑如下：
    1. 如果用户之前没有点过"踩"
        1.1 如果用户之前没有点过"赞"，则点赞记录+1，评论点赞数+1
        1.2 如果用户之前点过"赞"，则取消之前的点赞，删除之前的点赞记录，评论点赞数-1
    2. 如果用户之前点过"踩"
        删除之前的点"踩"记录，增加新的点赞记录
    :return:
    """
    cmt_id = request.form.get("cmt_id")
    up_id = session["thumb_up_id"]
    down_id = session["thumb_down_id"]
    user_id = session["user_id"]
    article_id = session["article_id"]

    cmt = Comment.query.get(cmt_id)
    down_record = UserCmtTag.query.filter_by(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag_id=down_id).first()
    if down_record is None:  # 如果用户之前没有点"踩"
        up_record = UserCmtTag.query.filter_by(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag_id=up_id).first()
        if up_record is None:  # 如果用户之前也没有点过"赞"
            new_up_record = UserCmtTag(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag_id=up_id)
            db.session.add(new_up_record)
            cmt.thumb_up += 1
        else:  # 如果点过"赞"，则取消之前的点赞
            db.session.delete(up_record)
            cmt.thumb_up -= 1
    else:  # 如果用户之前点过了"踩"
        cmt.thumb_down -= 1
        db.session.delete(down_record)  # 先删除"踩"的记录
        new_up_record = UserCmtTag(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag_id=up_id)
        db.session.add(new_up_record)  # 再新增"赞"的记录
        cmt.thumb_up += 1

    db.session.commit()

    return jsonify({"num": Comment.query.get(cmt_id).thumb_up})


@cmt_bp.route("/thumb_down_action", methods=["POST"])
@cross_origin()
def thumb_down_action():
    """
    整体逻辑如下：
    1. 如果用户之前没有点过"赞"
        1.1 如果用户之前没有点过"踩"，则点踩记录+1，评论点踩数+1
        1.2 如果用户之前点过"踩"，则删除之前的点踩记录，评论点踩数-1
    2. 如果用户之前点过"赞"
        删除之前的点"赞"记录，增加新的点踩记录
    :return:
    """
    cmt_id = request.form.get("cmt_id")
    up_id = session["thumb_up_id"]
    down_id = session["thumb_down_id"]
    user_id = session["user_id"]
    article_id = session["article_id"]

    cmt = Comment.query.get(cmt_id)
    up_record = UserCmtTag.query.filter_by(user_id=user_id, cmt_id=cmt_id, tag_id=up_id).first()
    if up_record is None:  # 如果用户之前没有点"赞"
        down_record = UserCmtTag.query.filter_by(user_id=user_id, cmt_id=cmt_id, tag_id=down_id).first()
        if down_record is None:  # 如果用户之前也没有点过"踩"
            new_down_record = UserCmtTag(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag_id=down_id)
            db.session.add(new_down_record)
            cmt.thumb_down += 1
        else:  # 如果点过"踩"，则取消之前的点"踩"
            db.session.delete(down_record)
            cmt.thumb_down -= 1
    else:  # 如果用户之前点过了"赞"
        cmt.thumb_up -= 1
        db.session.delete(up_record)  # 先删除"赞"的记录
        new_down_record = UserCmtTag(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag_id=down_id)
        db.session.add(new_down_record)  # 再新增"踩"的记录
        cmt.thumb_down += 1

    return jsonify({"num": Comment.query.get(cmt_id).thumb_down})


@cmt_bp.route("/tag_mark", methods=["POST"])
def tag_mark():
    cmt_id = request.form.get("cmt_id")
    tag_name = request.form.get("tag_name")
    user_id = session["user_id"]
    article_id = session["article_id"]

    target_tag = Tag.query.filter_by(tag_name=tag_name).first()
    if target_tag is None:  # 如果这是一个新标签
        # 添加新标签到Tag表
        target_tag = Tag(tag_name)
        db.session.add(target_tag)

        # 将打标签记录插入到comment_tag表
        new_ct = CommentTag(article_id=article_id, cmt_id=cmt_id, tag=target_tag)
        db.session.add(new_ct)

        # 将打标签的行为添加到user_cmt_tag表
        new_uct = UserCmtTag(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag=target_tag)
        db.session.add(new_uct)
    else:  # 如果这不是一个新标签
        # 则查看该评论是否已经打上了该标签
        cmt_tag = CommentTag.query.filter_by(cmt_id=cmt_id, tag_id=target_tag.id).first()
        if cmt_tag is None:  # 之前没有用户为该评论添加过此标签，创建一条新纪录
            new_ct = CommentTag(article_id=article_id, cmt_id=cmt_id, tag_id=target_tag.id)
            db.session.add(new_ct)
            # 同时创建一条用户标签记录
            new_uct = UserCmtTag(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag_id=target_tag.id)
            db.session.add(new_uct)
        else:  # 之前有用户为该评论添加过此标签
            # 查看当前用户是否支持过该标签
            uct = UserCmtTag.query.filter_by(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag_id=target_tag.id)
            if uct is None:  # 该用户之前没有支持过该标签
                cmt_tag.num += 1
                new_uct = UserCmtTag(article_id=article_id, user_id=user_id, cmt_id=cmt_id, tag_id=target_tag.id)
                db.session.add(new_uct)
            # 如果用户之前支持过或为该评论打过该标签，则什么都不做

    db.session.commit()
    return redirect(url_for("comment.index"))


@cmt_bp.route("/tag_agree", methods=["POST"])
@cross_origin()
def tag_agree():
    cmt_tag_id = request.form.get("cmt_tag_id")
    user_id = session["user_id"]
    article_id = session["article_id"]

    # 在表comment_tag中找到这条标签记录
    ct = CommentTag.query.get(cmt_tag_id)
    # 在表user_cmt_tag中搜索该用户是否支持过该标签
    uct = UserCmtTag.query.filter_by(article_id=article_id, user_id=user_id, cmt_id=ct.cmt_id, tag_id=ct.tag_id).first()
    if uct is None:  # 如果该用户没有支持过该标签
        new_uct = UserCmtTag(article_id=article_id, user_id=user_id, cmt_id=ct.cmt_id, tag_id=ct.tag_id)
        db.session.add(new_uct)
        ct.num += 1
        db.session.commit()
    else:  # 如果该用户支持过该标签
        db.session.delete(uct)  # 取消支持
        ct.num -= 1
        db.session.commit()
        # 如果标签的支持数变为了0，则删除该评论的该标签记录
        ct = CommentTag.query.get(cmt_tag_id)
        if ct.num == 0:
            db.session.delete(ct)
            db.session.commit()

    result = CommentTag.query.get(cmt_tag_id)
    return jsonify({"num": result.num if result is not None else 0})


################## TEST #########################
@cmt_bp.route("/test")
def test():
    return render_template("comment/test.html")


@cmt_bp.route("/base_test")
def base_test():
    return render_template("comment/base_test.html", nums=range(10))
