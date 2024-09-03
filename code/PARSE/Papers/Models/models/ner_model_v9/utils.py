"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 8/20/2022 2:33 AM
"""

import csv
import numpy as np
from config import Config
import pandas as pd

config = Config(mode="ssh")
def get_sep(data_file_name):
    with open(data_file_name, 'r', encoding='utf-8') as f:
        sample = f.read(1024)

    sniffer = csv.Sniffer()
    delimiter = sniffer.sniff(sample).delimiter
    return delimiter

# def load_data(data_file_name, min_seq_length):
#     with open(data_file_name, 'r', encoding='utf-8') as f:
#         text_lines = []
#         words = ""
#         labels = ""
#         df = pd.read_csv(f, names=['words', 'labels'], sep=get_sep(data_file_name), skip_blank_lines=False)
#         cur_length = 0
#         for index, row in df.iterrows():
#             if row['labels'] is np.nan:
#                 if cur_length >= min_seq_length:
#                     line = [labels.strip(), words.strip()]
#                     text_lines.append(line)
#                 words = ""
#                 labels = ""
#                 cur_length = 0
#             else:
#                 words += str(row['words']) + ' '
#                 labels += row['labels'] + ' '
#                 cur_length += 1
#     return text_lines

def load_data(data_file_name, min_seq_length):
    with open(data_file_name, 'r', encoding='utf-8') as f:
        text_lines = []
        words = ""
        labels = ""
        df = pd.read_csv(f, names=['words', 'labels'], sep=get_sep(data_file_name), skip_blank_lines=False)
        cur_length = 0
        for row in df.iterrows():
            cur_length += 1
            if cur_length >= min_seq_length and row[1]['words'] == '.':
                words += str(row[1]['words'])
                labels += row[1]['labels']
                line = [labels, words]
                words = ""
                labels = ""
                text_lines.append(line)
                cur_length = 0
            elif cur_length >= int(config.max_sequence_length * 0.8) and row[1]['labels'] == 'O':
                words += str(row[1]['words'])
                labels += row[1]['labels']
                line = [labels, words]
                words = ""
                labels = ""
                text_lines.append(line)
                cur_length = 0
            elif row[1]['labels'] is np.nan:
                cur_length = 0
            else:
                words += str(row[1]['words'])
                words += ' '
                labels += row[1]['labels']
                labels += ' '
    return text_lines

def get_labels():
    return Config(mode="ssh").tags

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

def get_data(data_file, min_seq_length):
    lines = load_data(data_file, min_seq_length)
    data = create_data(lines)
    return data

class DataLoader(object):

    def __init__(self, batch_size, data_file, tokenizer, pretrained_model=False, max_seq_length=100, is_test=False):
        self.data_file = data_file
        self.batch_size = batch_size
        self.max_seq_length = max_seq_length
        # self.min_seq_length = int(max_seq_length * 0.85)
        self.min_seq_length = 3
        self.data = get_data(data_file, self.min_seq_length)
        self.pretrained_model = pretrained_model

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

    def convert_single_example(self, example_idx, max_seq_length_in_batch):
        text_list = self.data[example_idx].text.rstrip().split(" ")
        label_list = self.data[example_idx].label.rstrip().split(" ")
        tokens = text_list
        labels = label_list

        if len(tokens) >= self.max_seq_length - 1:
            tokens = tokens[:(self.max_seq_length - 2)]
            labels = labels[:(self.max_seq_length - 2)]

        processed_tokens = ['[CLS]']
        segment_ids = [0]
        label_ids = [self.label_map['[CLS]']]

        for token, label in zip(tokens, labels):
            try:
                lower_token = token.lower()
                tokenized_word = self.tokenizer.tokenize(lower_token)
                processed_tokens.append(tokenized_word[0])
            except:
                processed_tokens.append('[UNK]')
            segment_ids.append(0)
            label_ids.append(self.label_map.get(label))

        processed_tokens.append("[SEP]")
        segment_ids.append(0)
        label_ids.append(self.label_map["[SEP]"])

        text_ids = self.tokenizer.convert_tokens_to_ids(processed_tokens)
        text_mask = [1] * len(text_ids)
        char_ids = [[config.char2idx.get(c, config.char2idx['[UNK]']) for c in token] for token in processed_tokens]

        diff_to_max_len = max_seq_length_in_batch - len(text_ids)
        if diff_to_max_len != 0:
            text_ids.extend([0] * diff_to_max_len)
            text_mask.extend([0] * diff_to_max_len)
            segment_ids.extend([0] * diff_to_max_len)
            label_ids.extend([self.label_map["[PAD]"]] * diff_to_max_len)
            processed_tokens.extend(["*NULL*"] * diff_to_max_len)
            tokens.extend(["*NULL*"] * diff_to_max_len)
            char_ids.extend([[config.char2idx["[PAD]"]] * len(char_ids[0])] * diff_to_max_len)

        return text_ids, text_mask, segment_ids, label_ids, processed_tokens, char_ids

    def shuffle(self):
        np.random.shuffle(self.all_idx)

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx >= self.num_records:
            self.idx = 0
            raise StopIteration

        current_batch_indices = self.all_idx[self.idx:self.idx + self.batch_size]
        max_seq_length_in_batch = 0

        for idx in current_batch_indices:
            text_list = self.data[idx].text.rstrip().split(" ")
            tokens = text_list
            if len(tokens) >= self.max_seq_length - 1:
                tokens = tokens[:(self.max_seq_length - 2)]
            max_seq_length_in_batch = max(max_seq_length_in_batch, len(tokens) + 2)  # Add 2 for [CLS] and [SEP] tokens

        examples = []
        num_tags = 0
        while num_tags < self.batch_size:
            idx = self.all_idx[self.idx]
            res = self.convert_single_example(idx, max_seq_length_in_batch)
            if res is None:
                self.idx += 1
                if self.idx >= self.num_records:
                    break
                continue
            examples.append(res)

            if self.pretrained_model:
                num_tags += 1

            self.idx += 1
            if self.idx >= self.num_records:
                break

        max_seq_length_in_batch = max([len(example[0]) for example in examples])

        # Find the maximum word length in the batch
        max_word_length_in_batch = 0
        for example in examples:
            max_word_length_in_example = max([len(char_ids) for char_ids in example[-1]])
            max_word_length_in_batch = max(max_word_length_in_batch, max_word_length_in_example)

        text_ids_list = []
        text_mask_list = []
        segment_ids_list = []
        label_ids_list = []
        tokens_list = []
        char_ids_list = []

        for example in examples:
            text_ids, text_mask, segment_ids, label_ids, tokens, char_ids = example

            # Pad the char_ids to make them have the same length
            char_ids_padded = [
                word_char_ids + [config.char2idx["[PAD]"]] * (max_word_length_in_batch - len(word_char_ids))
                for word_char_ids in char_ids]

            text_ids_list.append(text_ids)
            text_mask_list.append(text_mask)
            segment_ids_list.append(segment_ids)
            label_ids_list.append(label_ids)
            tokens_list.append(tokens)
            char_ids_list.append(char_ids_padded)  # Use the padded char_ids

        return text_ids_list, text_mask_list, segment_ids_list, label_ids_list, tokens_list, char_ids_list


if __name__ == "__main__":
    from transformers import BertTokenizer

    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    data_loader = DataLoader(32, "../dataset/train_title_v3.csv", tokenizer, pretrained_model=True)

    # 记录循环中的最后一个样本
    last_sample = None

    # 添加计数器
    sample_counter = 0

    for text_ids_list, text_mask_list, segment_ids_list, label_ids_list, tokens_list in data_loader:
        last_sample = (text_ids_list, text_mask_list, segment_ids_list, label_ids_list, tokens_list)


    print("Sample", sample_counter + 1)
    print("Text IDs:", text_ids_list)
    print("Text Mask:", text_mask_list)
    print("Segment IDs:", segment_ids_list)
    print("Label IDs:", label_ids_list)
    print("Tokens:", tokens_list)
    print("\n")






