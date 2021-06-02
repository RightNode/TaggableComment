#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from math import ceil


# 加载标签字典
def load_tag_idx(filepath):
    tag_dict = dict()
    with open(filepath, "r") as fin:
        for line in fin:
            temp = line.strip().split(",")
            tag_dict[temp[0]] = int(temp[1])

    return tag_dict


UNLATTERS = ",.:，。： "


# 转化原始数据文件
def convert_data(filepath, tag_dict, savepath):
    """
    for file content like: happiness:asfdadsfasdf,adsfasdf,asdf
    """
    rst_list = []
    with open(filepath, "r") as fin:
        for line in fin.readlines():
            temp = line.strip()
            sep_idx = temp.find(":")
            tag = temp[:sep_idx]
            ctx = temp[sep_idx + 1:].strip(UNLATTERS)
            rst_list.append([tag_dict[tag], ctx])

    rst = pd.DataFrame(rst_list, columns=["tag", "ctx"])
    # rst.sort_values(by="tag", inplace=True)
    rst.to_csv(savepath, header=False, index=False, sep="\t")


def convert_data2(filepath, savepath):
    """
    for file content like: 0,asdfadsfa,s,d,f
    """
    rst_list = []
    with open(filepath, "r") as fin:
        for line in fin.readlines():
            line = line.strip()
            tag = int(line[:1])
            content = line[2:].strip().lstrip(UNLATTERS).replace(" ", "")
            if content == "" or content is None:
                continue
            rst_list.append([tag, content])

    rst = pd.DataFrame(rst_list, columns=["tag", "content"])
    rst.to_csv(savepath, header=False, index=False, sep="\t")


# 划分数据集
def split_data(filepath, savedir):
    org_data = pd.read_csv(filepath, header=None, sep="\t", names=["tags", "content"])
    train_data = pd.DataFrame(columns=["tags", "content"])
    valid_data = pd.DataFrame(columns=["tags", "content"])
    test_data = pd.DataFrame(columns=["tags", "content"])

    for tag in org_data["tags"].unique():
        temp_df = org_data[org_data["tags"] == tag]

        temp_train = temp_df.sample(frac=0.8, replace=False)
        train_data = train_data.append(temp_train)

        temp_left = temp_df[~temp_df.index.isin(temp_train.index)]

        temp_valid = temp_left.sample(frac=0.5, replace=False)
        valid_data = valid_data.append(temp_valid)

        test_data = test_data.append(temp_left[~temp_left.index.isin(temp_valid.index)])

    train_data = train_data.sample(frac=1)
    valid_data = valid_data.sample(frac=1)
    test_data = test_data.sample(frac=1)

    train_data.to_csv(savedir + "train.csv", header=False, index=False, sep="\t")
    valid_data.to_csv(savedir + "valid.csv", header=False, index=False, sep="\t")
    test_data.to_csv(savedir + "test.csv", header=False, index=False, sep="\t")


# 划分数据集
def split_data_1w(filepath, savedir):
    org_data = pd.read_csv(filepath, header=None, sep="\t", names=["tags", "content"])
    train_data = pd.DataFrame(columns=["tags", "content"])
    valid_data = pd.DataFrame(columns=["tags", "content"])
    test_data = pd.DataFrame(columns=["tags", "content"])

    total = org_data.shape[0]
    component = org_data["tags"].value_counts().sort_values().to_dict()
    vt_set = {k: ceil(v / total * 10000) for k, v in component.items()}
    vt_set[list(vt_set.keys())[-1]] = vt_set[list(vt_set.keys())[-1]] - (sum(vt_set.values()) - 10000)
    tvt_set = {k: [component[k] - 2 * vt_set[k], vt_set[k], vt_set[k]] for k, v in component.items()}

    for tag in component.keys():
        temp_df = org_data[org_data["tags"] == tag]

        temp_train = temp_df.sample(n=tvt_set[tag][0], replace=False)
        train_data = train_data.append(temp_train)

        temp_left = temp_df[~temp_df.index.isin(temp_train.index)]

        temp_valid = temp_left.sample(n=tvt_set[tag][1], replace=False)
        valid_data = valid_data.append(temp_valid)

        test_data = test_data.append(temp_left[~temp_left.index.isin(temp_valid.index)])

    train_data = train_data.sample(frac=1)
    valid_data = valid_data.sample(frac=1)
    test_data = test_data.sample(frac=1)

    train_data.to_csv(savedir + "train.csv", header=False, index=False, sep="\t")
    valid_data.to_csv(savedir + "valid.csv", header=False, index=False, sep="\t")
    test_data.to_csv(savedir + "test.csv", header=False, index=False, sep="\t")


def load_data2(filename):
    """加载数据
    单条格式：(文本, 标签id)
    """
    D = []
    with open(filename, encoding='utf-8') as f:
        for l in f:
            label, text = l.strip().split('\t')
            D.append((text, int(label)))
    return D


if __name__ == '__main__':
    # tag_dict = load_tag_idx("static/data/tag-idx.csv")  # 加载标签序号
    # convert_data("static/data/huati_filter_final_posts_no_sge.txt", tag_dict, "static/data/cvt_org_data.csv")  # 转换原始数据文件
    split_data("/Users/kevinwen/Downloads/weibo_7_moods/cvt_org_data.csv", "/Users/kevinwen/Downloads/weibo_7_moods/")  # 划分数据集

    # convert_data2("/Users/kevinwen/Downloads/simplifyweibo_4_moods/simplifyweibo_4_moods.csv",
    #               "/Users/kevinwen/Downloads/simplifyweibo_4_moods/weibo_4_moods.csv")
    # split_data_1w("/Users/kevinwen/Downloads/simplifyweibo_4_moods/weibo_4_moods.csv", "/Users/kevinwen/Downloads/simplifyweibo_4_moods/")

    # train_data = load_data2('/Users/kevinwen/Downloads/simplifyweibo_4_moods/train.csv')
    # train_data = load_data2('/Users/kevinwen/Downloads/simplifyweibo_4_moods/valid.csv')
    # train_data = load_data2('/Users/kevinwen/Downloads/simplifyweibo_4_moods/test.csv')
