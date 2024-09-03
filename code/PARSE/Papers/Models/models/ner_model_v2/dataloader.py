"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 8/20/2022 2:33 AM
"""
import csv

import numpy as np
from transformers import BertTokenizer

from config import Config
import pandas as pd
import csv

global_mode = ""

def get_sep(data_file_name):
    with open(data_file_name, 'r', encoding='utf-8') as f:
        sample = f.read(1024)

    sniffer = csv.Sniffer()
    delimiter = sniffer.sniff(sample).delimiter
    return delimiter


def load_data(data_file_name):
    with open(data_file_name, 'r', encoding='utf-8') as f:
        text_lines = []
        words = []
        labels = []
        df = pd.read_csv(f, names=['words', 'labels'], sep=get_sep(data_file_name), skip_blank_lines=False)
        cur_length = 0
        for row in df.iterrows():
            cur_length += 1
            if pd.isna(row[1]['words']):
                line = [' '.join(labels), ' '.join(words)]
                words = []
                labels = []
                if line[0] != "" and line[1] != "":
                    text_lines.append(line)
                cur_length = 0
            elif row[1]['words'] == '.':
                words.append(str(row[1]['words']))
                labels.append(str(row[1]['labels']))
                line = [' '.join(labels), ' '.join(words)]
                words = []
                labels = []
                text_lines.append(line)
                cur_length = 0
            else:
                words.append(str(row[1]['words']))
                labels.append(str(row[1]['labels']))
    return text_lines



def get_labels():
    return Config(global_mode).tags

class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text, label=None):
        self.guid = guid
        self.text = text
        self.label = label


def create_data(data_file):
    data = []
    cnt = 0
    for line in data_file:
        guid = str(cnt)
        label = line[0]
        text = line[1]
        input_example = InputExample(guid=guid, text=text, label=label)
        data.append(input_example)
        cnt += 1
    return data

def get_data(data_file):
    lines = load_data(data_file)
    data = create_data(lines)
    return data

class DataLoader(object):

    def __init__(self, config, data_file, tokenizer, mode, is_test=False):
        self.config = config
        self.data_file = data_file
        self.batch_size = config.batch_size
        self.max_seq_length = config.max_sequence_length
        self.data = get_data(data_file)
        self.pretrained_model = config.pretrained_model
        global_mode = mode
        self.num_records = len(self.data)
        self.all_tags = []
        self.idx = 0
        self.all_idx = list(range(self.num_records))
        self.is_test = is_test

        # if not self.is_test:
        #     self.shuffle()
        self.tokenizer = tokenizer
        self.label_map = {}
        for index, label in enumerate(get_labels()):
            self.label_map[label] = index
        print("label numbers: ", len(get_labels()))
        print("sample numbers: ", self.num_records)

    def convert_single_example(self, example_idx, max_length_sents):
        text_list = self.data[example_idx].text.split(" ")
        label_list = self.data[example_idx].label.split(" ")
        tokens = text_list
        labels = label_list

        if len(tokens) != len(labels):
            print("Warning: Skipping example with index {} due to length mismatch between tokens and labels.".format(
                example_idx))
            return None

        # if seq_length=64, the max text length will be 62
        # <cls>text<sep>
        if len(tokens) >= self.max_seq_length - 1:
            tokens = tokens[:(self.max_seq_length - 2)]
            labels = labels[:(self.max_seq_length - 2)]
        processed_tokens = []
        segment_ids = []
        label_ids = []

        processed_tokens.append('[CLS]')
        segment_ids.append(0)
        label_ids.append(self.label_map['[CLS]'])

        for index, token in enumerate(tokens):
            try:
                lower_token = token.lower()
                tokenized_word = self.tokenizer.tokenize(lower_token)
                processed_tokens.append(tokenized_word[0])
            except:
                processed_tokens.append('[UNK]')
            segment_ids.append(0)
            label_ids.append(self.label_map.get(labels[index]))
            if self.label_map.get(labels[index]) == None:
                print(labels[index])



        token_list = ["[CLS]"]
        token_list.extend(tokens)
        token_list.extend(["[SEP]"])
        tokens = token_list
        processed_tokens.append("[SEP]")
        segment_ids.append(0)
        label_ids.append(self.label_map["[SEP]"])

        text_ids = self.tokenizer.convert_tokens_to_ids(processed_tokens)
        text_mask = [1] * len(text_ids)

        diff_to_max_len = max_length_sents - len(text_ids)
        if diff_to_max_len != 0:
            text_ids.extend([0] * diff_to_max_len)
            text_mask.extend([0] * diff_to_max_len)
            segment_ids.extend([0] * diff_to_max_len)
            label_ids.extend([self.label_map["[PAD]"]] * diff_to_max_len)
            processed_tokens.extend(["*NULL*"] * diff_to_max_len)
            tokens.extend(["*NULL*"] * diff_to_max_len)
        return text_ids, text_mask, segment_ids, label_ids, tokens

    def shuffle(self):
        np.random.shuffle(self.all_idx)

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx >= self.num_records:
            self.idx = 0
            if not self.is_test:
                self.shuffle()
            raise StopIteration

        text_ids_list = []
        text_mask_list = []
        segment_ids_list = []
        label_ids_list = []
        tokens_list = []

        num_tags = 0

        # get the longest sentence length in  current batch
        sents_length = []
        index = self.idx
        while index < self.num_records and len(sents_length) < self.batch_size:
            real_ind = self.all_idx[index]
            sents_length.append(len(self.data[real_ind].label.split(" ")))
            index += 1
        max_length_sents = max(sents_length) + 2

        while num_tags < self.batch_size:

            idx = self.all_idx[self.idx]
            res = self.convert_single_example(idx, max_length_sents)
            if res is None:
                self.idx += 1
                if self.idx >= self.num_records:
                    break
                continue
            text_ids, text_mask, segment_ids, label_ids, tokens = res

            text_ids_list.append(text_ids)
            text_mask_list.append(text_mask)
            segment_ids_list.append(segment_ids)
            label_ids_list.append(label_ids)
            tokens_list.append(tokens)

            if self.pretrained_model:
                num_tags += 1

            self.idx += 1
            if self.idx >= self.num_records:
                break

        diff_to_batch_size = self.batch_size - len(text_ids_list)
        if diff_to_batch_size != 0:
            text_ids_list.extend([text_ids_list[0]]*diff_to_batch_size)
            text_mask_list.extend([text_mask_list[0]]*diff_to_batch_size)
            segment_ids_list.extend([segment_ids_list[0]]*diff_to_batch_size)
            label_ids_list.extend([label_ids_list[0]]*diff_to_batch_size)
            tokens_list.extend([tokens_list[0]]*diff_to_batch_size)

        return text_ids_list, text_mask_list, segment_ids_list, label_ids_list, tokens_list


if __name__ == '__main__':
    config = Config(mode="local")
    tokenizer = BertTokenizer.from_pretrained(config.model_dir,
                                              do_lower_case=True,
                                              never_split=["[UNK]", "[SEP]", "[PAD]", "[CLS]", "[MASK]"])
    train_dataloader = DataLoader(config,
                                  data_file="../dataset/train_title.csv",
                                  tokenizer=tokenizer, mode = "local")
    for text_ids_list, text_mask_list, segment_ids_list, label_ids_list, tokens_list in train_dataloader:
        temp = np.array(text_ids_list)




