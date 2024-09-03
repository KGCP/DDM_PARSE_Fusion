"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 26/9/2022 10:48 pm
"""
import json
import os
import numpy as np
from pandas import DataFrame
from tqdm import tqdm
from transformers import BertTokenizer, AutoTokenizer, DebertaTokenizer, BertConfig
from config import Config
import logging
import torch
from ner_model import BertForNameEntityRecognition
from dataloader import DataLoader

#sys.path.append('/Users/bowenzhang/Library/CloudStorage/OneDrive-個人/Programming/PycharmProjects/anu-scholarly-kg/src/Papers/Models/models/nel_models')

config = Config()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def list2ts2device(target_list):
    target_ts = torch.from_numpy(np.array(target_list))
    return target_ts.to(device)


def end_of_chunk(prev_tag, tag, prev_type, type_):
    """Checks if a chunk ended between the previous and current word.

    Args:
        prev_tag: previous chunk tag.
        tag: current chunk tag.
        prev_type: previous type.
        type_: current type.

    Returns:
        chunk_end: boolean.
    """
    chunk_end = False

    if prev_tag == 'E': chunk_end = True
    if prev_tag == 'S': chunk_end = True

    if prev_tag == 'B' and tag == 'B': chunk_end = True
    if prev_tag == 'B' and tag == 'S': chunk_end = True
    if prev_tag == 'B' and tag == 'O': chunk_end = True
    if prev_tag == 'I' and tag == 'B': chunk_end = True
    if prev_tag == 'I' and tag == 'S': chunk_end = True
    if prev_tag == 'I' and tag == 'O': chunk_end = True

    if prev_tag != 'O' and prev_tag != '.' and prev_type != type_:
        chunk_end = True

    return chunk_end


def start_of_chunk(prev_tag, tag, prev_type, type_):
    """Checks if a chunk started between the previous and current word.

    Args:
        prev_tag: previous chunk tag.
        tag: current chunk tag.
        prev_type: previous type.
        type_: current type.

    Returns:
        chunk_start: boolean.
    """
    chunk_start = False

    if tag == 'B': chunk_start = True
    if tag == 'S': chunk_start = True

    if prev_tag == 'E' and tag == 'E': chunk_start = True
    if prev_tag == 'E' and tag == 'I': chunk_start = True
    if prev_tag == 'S' and tag == 'E': chunk_start = True
    if prev_tag == 'S' and tag == 'I': chunk_start = True
    if prev_tag == 'O' and tag == 'E': chunk_start = True
    if prev_tag == 'O' and tag == 'I': chunk_start = True

    if tag != 'O' and tag != '.' and prev_type != type_:
        chunk_start = True

    return chunk_start

def get_entities(seq, suffix=False):
    if any(isinstance(s, list) for s in seq):
        seq = [item for sublist in seq for item in sublist + ['O']]

    prev_tag = 'O'
    prev_type = ''
    begin_offset = 0
    chunks = []
    for i, chunk in enumerate(seq + ['O']):
        if suffix:
            tag = chunk[-1]
            type_ = chunk.split('-')[0]
        else:
            tag = chunk[0]
            type_ = chunk.split('-')[-1]

        if end_of_chunk(prev_tag, tag, prev_type, type_):
            chunks.append((prev_type, begin_offset, i - 1))
        if start_of_chunk(prev_tag, tag, prev_type, type_):
            begin_offset = i
        prev_tag = tag
        prev_type = type_

    return chunks


def get_entity_dict(pred_tags, tokens_list, input_mask, result_dict, accu_words):
    pred_result = []
    cur_accu_word = 0
    for idx, line in enumerate(pred_tags):
        entities = get_entities(line)
        sample_dict = {}
        for entity in entities:
            label_type = entity[0]
            if label_type == '[CLS]' or label_type == '[SEP]':
                continue
            start_ind = entity[1]
            end_ind = entity[2]
            # get the entity
            entity = ""
            entity_len = end_ind + 1 - start_ind
            for i in range(entity_len):
                entity += tokens_list[idx][start_ind + i] + " "
            entity = entity.strip()

            if entity in ["[CLS]", "[SEP]", "[UNK]"]:
                continue

            if entity not in result_dict[label_type].keys():
                result_dict[label_type][entity] = {}

            # locate word position in the paper
            abs_start_pos = accu_words + cur_accu_word + start_ind - 1
            abs_end_pos = accu_words + cur_accu_word + end_ind - 1
            result_dict[label_type][entity]["position"] = []
            result_dict[label_type][entity]["position"].append((abs_start_pos, abs_end_pos))

            if label_type in sample_dict.keys():
                sample_dict[label_type].append(''.join(entity))
            else:
                sample_dict[label_type] = [''.join(entity)]

        real_len = int(input_mask[idx].sum())
        cls_num = tokens_list[idx].count("[CLS]")
        sep_num = tokens_list[idx].count("[SEP]")
        unk_num = tokens_list[idx].count("[UNK]")
        cur_accu_word = cur_accu_word + real_len - cls_num - sep_num - unk_num
        pred_result.append(sample_dict)

    return pred_result


def get_predicted_text(pred, tokens, word_list, label_list):
    for idx in range(len(pred)):
        for i in range(len(pred[idx])):
            if tokens[idx][i] in ["[CLS]", "[SEP]", "[UNK]"]:
                continue
            else:
                label_list.append(pred[idx][i])
                word_list.append(tokens[idx][i])


def get_entity(words_list, label_list, result_dict):
    i = 0
    while i < len(words_list):
        if label_list[i] not in ["O", "[CLS]", "[UNK]", "[SEP]"]:
            pointer = i
            entity = ""
            seq, label = label_list[i].split("-")
            entity += words_list[i]
            word_cnt = 1
            while True:
                pointer += 1
                if label_list[pointer] in ["[CLS]", "[UNK]", "[SEP]", "O"]:
                    break
                seq_next, _ = label_list[pointer].split("-")
                entity += " " + words_list[pointer]
                if seq_next != "I":
                    break
                word_cnt += 1
            if entity not in result_dict[label].keys():
                result_dict[label][entity] = {}
                result_dict[label][entity]["position"] = []
                result_dict[label][entity]["sentence"] = []
            result_dict[label][entity]["position"].append([i, pointer-1])
            i = pointer
        else:
            i += 1
    return result_dict


def get_original_sentence(words_list, result_dict):
    for key in result_dict.keys():
        for entity in result_dict[key]:
            sentence = []
            pos = result_dict[key][entity]["position"]
            if len(pos) > 0:
                for p in pos:
                    l_pointer = p[0]
                    sentence.extend(words_list[p[0]:p[1]+1])
                    # add left part sentence
                    while True:
                        l_pointer -= 1
                        limit = 15
                        if l_pointer < 0 or words_list[l_pointer] == "." or p[0]-l_pointer > limit:
                            break
                        else:
                            sentence.insert(0, words_list[l_pointer])
                    r_pointer = p[1]
                    while True:
                        r_pointer += 1
                        limit = 15
                        if r_pointer > len(words_list) or words_list[r_pointer] == "." or r_pointer - p[1] > limit:
                            break
                        else:
                            sentence.append(words_list[r_pointer])
                    sentence_str = ""
                    for s in sentence:
                        sentence_str += s + " "
                    sentence_str = sentence_str.strip().lower()
                    result_dict[key][entity]["sentence"].append(sentence_str)

def predict(pred_dataloader, model_path):
    # remove map_lcation
    state_dict = torch.load(model_path, map_location=torch.device('cpu'))
    # state_dict = torch.load(model_path)
    bert_config = BertConfig.from_pretrained(config.pretrained_model_config, output_hidden_states=True)
    model = BertForNameEntityRecognition.from_pretrained(config=bert_config,
                                                             pretrained_model_name_or_path=config.model_dir)
    model.load_state_dict(state_dict)
    model.to(device)
    logger.info("******** Running Prediction ********")
    model.eval()
    labels = config.tags
    idx2tag = dict(zip(range(len(labels)), labels))
    pred_answer = []
    true_tags, pred_tags = [], []
    result_dict = {}
    for c in config.tag_class:
        result_dict[c] = {}
    iter_num = 0
    words_list = []
    label_list = []
    for input_ids_list, input_mask_list, segment_ids_list, label_ids_list, tokens_list in tqdm(pred_dataloader):
        input_ids = list2ts2device(input_ids_list)
        input_mask = list2ts2device(input_mask_list)
        segment_ids = list2ts2device(segment_ids_list)
        batch_output = model(input_ids=input_ids, token_type_ids=segment_ids, attention_mask=input_mask)

        real_batch_tags = []
        for i in range(config.batch_size):
            real_len = int(input_mask[i].sum())
            real_batch_tags.append(label_ids_list[i][:real_len])

        pred_tags.extend([idx2tag.get(idx) for indices in batch_output for idx in indices])
        pred = [[idx2tag.get(idx) for idx in indices] for indices in batch_output]
        # get_entity_dict(pred, tokens_list, input_mask, result_dict, accu_words)
        get_predicted_text(pred, tokens_list, words_list, label_list)
        iter_num += 1

    get_entity(words_list, label_list, result_dict)
    get_original_sentence(words_list, result_dict)


    dict_path = os.path.join(config.predict_dict_output_path, "test_dict.json")
    with open(dict_path, 'w') as f:
        json.dump(result_dict, f)

    temp = {
        "text": words_list,
        "label": label_list
    }
    df = DataFrame(temp)
    text_path = os.path.join(config.predict_text_output_path, "test_predicted_text1.csv")
    df.to_csv(text_path, index=False)

if __name__ == '__main__':
    config = Config()
    if config.pretrained_model == "bert":
        tokenizer = BertTokenizer.from_pretrained(config.model_dir,
                                                  do_lower_case=True,
                                                  never_split=["[UNK]", "[SEP]", "[PAD]", "[CLS]", "[MASK]"])
    elif config.pretrained_model == "xlm_roberta":
        tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-base',
                                                  do_lower_case=True,
                                                  never_split=["[UNK]", "[SEP]", "[PAD]", "[CLS]", "[MASK]"]
                                                  )
    elif config.pretrained_model == "roberta":
        tokenizer = AutoTokenizer.from_pretrained('roberta-base',
                                                  do_lower_case=True,
                                                  never_split=["[UNK]", "[SEP]", "[PAD]", "[CLS]", "[MASK]"]
                                                  )
    elif config.pretrained_model == "deberta":
        tokenizer = DebertaTokenizer.from_pretrained("microsoft/deberta-base",
                                                     do_lower_case=True,
                                                     never_split=["[UNK]", "[SEP]", "[PAD]", "[CLS]", "[MASK]"]
                                                     )
    else:
        raise Exception("tokenizer not defined")

    #1607.08822.csv;1711.07280.csv
    dev_dataloader = DataLoader(config.batch_size,
                                  data_file=os.path.join(config.processed_data, '1607.08822.csv'),
                                  tokenizer=tokenizer, is_test=True,
                                max_seq_length=config.max_sequence_length,
                                pretrained_model=config.pretrained_model)
    predict(dev_dataloader, config.predict_model_path)


