#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import re

import keras
from bert4keras.models import build_transformer_model
from bert4keras.optimizers import extend_with_piecewise_linear_lr, Adam
from bert4keras.snippets import DataGenerator, sequence_padding
from bert4keras.tokenizers import Tokenizer
from keras.layers import Lambda, Dense

from utils.model_utils import load_data


# 还需要根据albert_test.ipynb修改
class CmtClassifier:

    def __init__(self, model_type, model_para_paths, label_filepath, origin):
        # 属性赋值
        self.model_type = model_type
        self.model_para_paths = model_para_paths
        self.label_filepath = label_filepath

        # 加载编号-标签字典
        with open(label_filepath, "r") as fin:
            reader = csv.reader(fin)
            self.label_dict = {int(row[0]): row[1] for row in reader}

        # 创建分词器
        self.tokenizer = Tokenizer(model_para_paths[2], do_lower_case=True)

        if origin:  # 表示构建一个还未经过微调的模型
            # 模型的上游
            bert = build_transformer_model(
                config_path=model_para_paths[0],
                checkpoint_path=model_para_paths[1],
                model=model_type,
                return_keras_model=False,
            )
            # 取[CLS]这个token的输出向量作为下游任务的输入
            output = Lambda(lambda x: x[:, 0], name='CLS-token')(bert.model.output)
            # 模型的下游
            output = Dense(
                units=len(self.label_dict),
                activation='softmax',
                kernel_initializer=bert.initializer
            )(output)
            # 连接模型的输入与输出
            self.model = keras.models.Model(bert.model.input, output)
        else:  # 表示模型已经过微调
            self.model = build_transformer_model(
                config_path=model_para_paths[0],
                checkpoint_path=model_para_paths[1],
                model=model_type,
                return_keras_model=False,
            )
        self.model.summary()  # 显示模型结构

    def fit(self, train_filepath, valid_filepath, temp_save_path,
            maxlen=128, learning_rate=1e-4, epochs=5, batch_size=32):
        train_data = load_data(train_filepath)
        train_generator = CmtDataGenerator(train_data, batch_size, self.tokenizer)

        callbacks = None
        if valid_filepath != "" and valid_filepath is not None \
                and temp_save_path != "" and temp_save_path is not None:
            valid_data = load_data(valid_filepath)
            valid_generator = CmtDataGenerator(valid_data, batch_size, self.tokenizer)
            evaluator = Evaluator(self.model, valid_generator, temp_save_path)
            callbacks = [evaluator]

        AdamLR = extend_with_piecewise_linear_lr(Adam, name='AdamLR')

        self.model.compile(
            loss='sparse_categorical_crossentropy',
            optimizer=AdamLR(learning_rate=learning_rate, lr_schedule={
                1000: 1,
                2000: 0.1
            }),
            metrics=['accuracy'],
        )

        self.model.fit(
            train_generator.forfit(),
            steps_per_epoch=len(train_generator),
            epochs=epochs,
            callbacks=callbacks
        )

        if callbacks is not None:
            self.model.load_weights(temp_save_path)

    def clean_data(self, input):
        at_pattern = re.compile("//@.*?:")
        url_pattern = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

        # 去掉Email和URL
        input = re.sub(at_pattern, "", input)
        input = re.sub(url_pattern, "", input)
        # 去掉首尾空格
        return input.strip()

    def predict(self, input):
        tids, sids = self.encode(self.clean_data(input), 128)
        y_pred = self.model.predict([tids, sids]).argmax(axis=1)
        return y_pred, self.label_dict[y_pred]

    def encode(self, input, maxlen=None):
        return self.tokenizer.encode(input, maxlen)

    def load_weights(self, param_path):
        self.model.load_weights(param_path)

    def save_model(self, savepath):
        self.model.save(savepath)


class Evaluator(keras.callbacks.Callback):
    """评估与保存
    """

    def __init__(self, model, data_generator, temp_path):
        self.model = model
        self.data = data_generator
        self.temp_path = temp_path
        self.best_val_acc = 0.

    def evaluate(self, data):
        total, right = 0., 0.
        for x_true, y_true in data:
            y_pred = self.model.predict(x_true).argmax(axis=1)
            y_true = y_true[:, 0]
            total += len(y_true)
            right += (y_true == y_pred).sum()
        return right / total

    def on_epoch_end(self, epoch, logs=None):
        val_acc = self.evaluate(self.data)

        if val_acc > self.best_val_acc:
            self.best_val_acc = val_acc
            self.model.save_weights(self.temp_path)


class CmtDataGenerator(DataGenerator):
    """数据生成器
    """

    def __init__(self, data, batch_size, tokenizer):
        super.__init__(data, batch_size)
        self.tokenizer = tokenizer

    def __iter__(self, random=False):
        batch_token_ids, batch_segment_ids, batch_labels = [], [], []
        for is_end, (text, label) in self.sample(random):
            token_ids, segment_ids = self.tokenizer.encode(text, maxlen=128)
            batch_token_ids.append(token_ids)
            batch_segment_ids.append(segment_ids)
            batch_labels.append([label])
            if len(batch_token_ids) == self.batch_size or is_end:
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_segment_ids = sequence_padding(batch_segment_ids)
                batch_labels = sequence_padding(batch_labels)
                yield [batch_token_ids, batch_segment_ids], batch_labels
                batch_token_ids, batch_segment_ids, batch_labels = [], [], []
