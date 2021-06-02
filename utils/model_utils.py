#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def load_data(filename):
    """加载数据
    单条格式：(文本, 标签id)
    """
    D = []
    with open(filename, encoding='utf-8') as f:
        for l in f:
            label, text = l.strip().split('\t')
            D.append((text, int(label)))
    return D
