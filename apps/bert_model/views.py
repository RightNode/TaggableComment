#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Blueprint

model_bp = Blueprint("model", __name__)


@model_bp.route("/update_model", methods=["POST"])
def update_model():
    pass
