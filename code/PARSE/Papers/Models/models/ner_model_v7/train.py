"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 8/15/2022 3:08 PM
"""
import copy
import json
import logging
import os
import random
import re
import time
import warnings
from collections import defaultdict
import torch
from sklearn.metrics import classification_report
import pickle
import torch.nn as nn
import numpy as np
from transformers import BertConfig, BertTokenizer, AlbertConfig, AdamW, get_linear_schedule_with_warmup, AutoTokenizer
from optimization import BertAdam
from config import Config
from ner_model import BertForNameEntityRecognition
from tqdm import tqdm
from utils import DataLoader

# mode = "ssh"
mode = "ssh"
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')
config = Config(mode)
n_gpu = torch.cuda.device_count()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
gpu_id = 1


class EarlyStopper(object):
    def __init__(self, min_step, max_step, patience, improve='up'):
        self.improve = improve
        self.best_scores = {
            'acc': 0,
            'f1': 0,
        }
        self.best_models = defaultdict(lambda: None)  # key: metric name; value: model
        self.increase_bool_tensor = defaultdict(lambda: torch.zeros(max_step).share_memory_())

        self.early_stop = torch.BoolTensor([False]).share_memory_()
        self.cur_step = 0
        self.best_step = {
            'acc': 0,
            'f1': 0,
        }
        self.min_step = max(min_step, patience)
        self.patience = patience

    def set_best_scores(self, best_scores: dict):
        self.best_scores.update(best_scores)
        self.best_step.update({k: 0 for k in best_scores.keys()})
        for metric_name in self.best_scores:
            self.increase_bool_tensor[metric_name][self.cur_step] = 0
            self.best_models[metric_name] = None

    def better(self, new_score, metric_name) -> bool:
        if self.improve == 'down':
            return new_score < self.best_scores[metric_name]

        if self.improve == 'up':
            return new_score > self.best_scores[metric_name]

    def update(self, updated_score: dict, updated_model):
        '''
        updated_score: dict key: metric name; value: score
        '''
        for metric_name, new_score in updated_score.items():
            if self.better(new_score=new_score, metric_name=metric_name):
                self.best_scores[metric_name] = new_score
                self.best_models[metric_name] = copy.deepcopy(updated_model)
                self.best_models[metric_name].cpu()
                self.increase_bool_tensor[metric_name][self.cur_step] = 1
                self.best_step[metric_name] = self.cur_step
        self.cur_step += 1

        self.check_stop()

    def check_stop(self, ):
        if self.cur_step <= self.min_step:
            self.early_stop[0] = False
        else:
            for metric_name, increase_bool_tensor in self.increase_bool_tensor.items():
                # improved = increase_bool_tensor[(self.cur_step - self.patience): self.cur_step].sum() != 0
                improved = increase_bool_tensor[(self.cur_step - self.patience): self.cur_step + 1].sum() != 0
                if improved:
                    break
            else:
                self.early_stop[0] = True

    def stopped(self):
        return self.early_stop.item()


def _extract_metrics_name(ckpt_file_name):
    pattern = re.compile(r'M\(.*?=')
    find = list(re.finditer(pattern, ckpt_file_name))
    if not find:
        return
    metric_name = str(find[0].group()[2:-1])
    return metric_name


def data2device(target_list):
    target_ts = torch.from_numpy(np.array(target_list))
    return target_ts.to(device)

def _extract_metrics_value(ckpt_file_name):
    pattern = re.compile(r'=.*?\)')
    find = list(re.finditer(pattern, ckpt_file_name))
    if not find:
        return
    metric_value = float(find[0].group()[2:-1])
    return metric_value


def evaluate(model, val_dataloader):
    if not val_dataloader.is_test:
        val_dataloader.is_test = True
    labels = config.tags
    id2tag = {}
    for id, label in enumerate(labels):
        id2tag[id] = label
    # set model to eval mode
    model.eval()
    with torch.no_grad():
        total_real_label = []
        total_pred_labels = []
    for text_ids_list, text_mask_list, segment_ids_list, label_ids_list, tokens_list in tqdm(val_dataloader):
        text_ids = data2device(text_ids_list)
        text_mask = data2device(text_mask_list)
        segment_ids = data2device(segment_ids_list)
        batch_output = model(input_ids=text_ids, token_type_ids=segment_ids, attention_mask=text_mask)

        real_batch_tag = []
        # for i in range(config.batch_size):
        for i in range(len(text_mask)):
            real_length = int(text_mask[i].sum())
            real_labels = label_ids_list[i][:real_length]
            real_batch_tag.append(real_labels)

        for output in batch_output:
            sub_pred_labels = [id2tag[id] for id in output]
            total_pred_labels.extend(sub_pred_labels)
        for real_id_list in real_batch_tag :
            real_labels_list = [id2tag[id] for id in real_id_list]
            total_real_label.extend(real_labels_list)

    target_eval_names = set(config.tags) - {"[PAD]", "[CLS]", "[SEP]", "O"}
    labels_eval_dict = classification_report(total_real_label, total_pred_labels, digits=4, output_dict=True)

    precision = 0
    recall = 0
    f1_score = 0

    for k in labels_eval_dict.keys():
        if k in target_eval_names:
            precision += labels_eval_dict.get(k).get('precision')
            recall += labels_eval_dict.get(k).get('recall')
            f1_score += labels_eval_dict.get(k).get('f1-score')
    f1_score = f1_score / len(target_eval_names)
    precision = precision / len(target_eval_names)
    recall = recall / len(target_eval_names)
    model.train()
    return precision, recall, f1_score

def train(train_dataloader, valid_dataloader):
    # initialize device
    logger.info('Initializing device...')
    if config.seed is not None:
        random.seed(config.seed)
        np.random.seed(config.seed)
        torch.manual_seed(config.seed)
        if n_gpu > 0:
            torch.cuda.manual_seed_all(config.seed)
    logger.info('\rInitialized device.')

    # initialize model
    logger.info('Initializing model...')
    if config.pretrained_model in ["BERT-base", "ALBERT", "ROBERTA", "SciBERT", "DEBERTA"]:
        bert_config = BertConfig.from_pretrained(config.pretrained_model_config, output_hidden_states=True)
        model = BertForNameEntityRecognition.from_pretrained(config=bert_config,
                                                             pretrained_model_name_or_path=config.model_dir)
    else:
        raise Exception("model not defined")

    bert_config.output_hidden_states = True
    model.to(device)

    # define if train from checkpoint
    if config.train_from_ckpt is not None:
        logger.info(f'Train from checkpoint {config.train_from_ckpt}.')
        state_dict = torch.load(os.path.join(config.train_from_ckpt))
        model.load_state_dict(state_dict)

    logger.info('\rInitialized model.')

    # initialize parameters
    logger.info('Initializing optimizer...')
    param_optimizer = list(model.named_parameters())
    pre_params = [(n, p) for n, p in param_optimizer if 'bert' in n]
    finetune_params = [(n, p) for n, p in param_optimizer if
                       not any([s in n for s in ('bert', 'crf', 'albert')]) or 'dym_weight' in n]

    no_decay = ['bias', 'LayerNorm', 'dym_weight', 'layer_norm']
    optimizer_params = [
        # pretrain model param
        {'params': [p for n, p in pre_params if not any(nd in n for nd in no_decay)],
         'weight_decay': config.decay_rate, 'lr': config.bert_learning_rate
         },
        {'params': [p for n, p in pre_params if any(nd in n for nd in no_decay)],
         'weight_decay': 0.0, 'lr': config.bert_learning_rate
         },
        # middle model
        {'params': [p for n, p in finetune_params if not any(nd in n for nd in no_decay)],
         'weight_decay': config.decay_rate, 'lr': config.general_learning_rate
         },
        {'params': [p for n, p in finetune_params if any(nd in n for nd in no_decay)],
         'weight_decay': 0.0, 'lr': config.general_learning_rate
         },
    ]
    num_training_steps = train_dataloader.num_records // config.gradient_accumulation_steps * config.train_epoch
    if config.optimizer == "BertAdam":
        # optimizer and scheduler is combined
        optimizer = BertAdam(optimizer_params, warmup=config.warmup_proportion, schedule="warmup_cosine",
                             t_total=num_training_steps)
        scheduler = None
    elif config.optimizer == "AdamW":
        # optimizer and scheduler is seperated
        optimizer = AdamW(optimizer_params, lr=config.general_learning_rate, weight_decay=config.weight_decay_rate)
        scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=100,
                                                    num_training_steps=num_training_steps)
    else:
        raise Exception("optimizer not defined")

    # initialize early stopper
    max_step = config.train_epoch * train_dataloader.num_records // config.train_epoch
    early_stopper = EarlyStopper(min_step=1, max_step=max_step, patience=config.patience, improve='up')
    best_scores = {'train_f1': 0, 'train_acc': 0, 'f1': 0, 'acc': 0, }
    early_stopper.set_best_scores(best_scores)
    if config.train_from_ckpt:
        ckpts = os.listdir(config.save_ckpt_path)
        m_names = [_extract_metrics_name(x) for x in ckpts]
        m_values = [_extract_metrics_value(x) for x in ckpts]
        early_stopper.set_best_scores({m_name: m_value for m_name, m_value in zip(m_names, m_values)})
    logger.info('\rInitialized optimizer.')

    # initialize multi gpu
    if n_gpu > 0:
        if n_gpu == 1:
            model.cuda(device=device)
        else:
            logger.info("initialize multi GPU...")
            device_names = [torch.cuda.get_device_name(device_id) for device_id in config.gpu]
            logger.info('Using devices: {}'.format(device_names))
            model = torch.nn.DataParallel(model, device_ids=config.gpu)
            model = model.cuda(device=device)
            logger.info("multi GPU initialized")

    # start training
    logger.info("*" * 10 + "Training Start" + "*" * 10)
    logger.info("  Batch size = %d", config.batch_size)
    logger.info("  Num epochs = %d", config.train_epoch)

    cum_step = 0
    timestamp = str(int(time.time()))
    out_dir = os.path.abspath(
        os.path.join(config.save_model, "runs_" + str(gpu_id), timestamp))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    print("Writing to {}\n".format(out_dir))

    draw_step_list = []
    draw_loss_list = []
    # initiate result recorder
    result_dict = {}
    res_dict_parameters = 'parameters'
    res_dict_train = "train"
    res_dict_test = "test"
    result_dict[res_dict_parameters] = {}
    result_dict[res_dict_train] = {}
    result_dict[res_dict_test] = {}

    result_dict[res_dict_parameters] = {
        "batch_size": config.batch_size,
        "max_sequence_length": config.max_sequence_length,
        "pretrained_model": config.pretrained_model,
        "optimizer": config.optimizer,
        "do_pgd": config.do_pgd,
        "general_learning_rate": config.general_learning_rate,
        "bert_learning_rate": config.bert_learning_rate,
        "weight_decay_rate": config.weight_decay_rate,
        "dropout_rate": config.dropout_rate,
        "decay_rate": config.decay_rate,
        "mid_struct": config.mid_struct,
        "warmup_proportion": config.warmup_proportion,
    }


    for i in range(config.train_epoch):
        model.train()
        for text_ids_list, text_mask_list, segment_ids_list, label_ids_list, tokens_list in tqdm(train_dataloader):
            input_ids = data2device(text_ids_list)
            token_type_ids = data2device(segment_ids_list)
            attention_mask = data2device(text_mask_list)
            labels = data2device(label_ids_list)
            loss = model(input_ids=input_ids, token_type_ids=token_type_ids,
                         attention_mask=attention_mask, labels=labels)
            if n_gpu > 1:
                loss = loss.mean()
            if config.gradient_accumulation_steps > 1:
                loss = loss / config.gradient_accumulation_steps

                if cum_step % 10 == 0:
                    draw_step_list.append(cum_step)
                    draw_loss_list.append(loss)

            loss.backward()
            if (cum_step + 1) % config.gradient_accumulation_steps == 0:
                # performs updates using calculated gradients
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
                model.zero_grad()
            cum_step += 1


        p, r, f1 = evaluate(model, valid_dataloader)
        print('validation set : step_{},precision_{}, recall_{}, F1_{}'.format(cum_step, p, r, f1))

        result_dict[res_dict_test][f'epoch{i}_step{cum_step}'] = {}
        result_dict[res_dict_test][f'epoch{i}_step{cum_step}']['precision'] = p
        result_dict[res_dict_test][f'epoch{i}_step{cum_step}']['recall'] = r
        result_dict[res_dict_test][f'epoch{i}_step{cum_step}']['f1'] = f1

        result_json_dir = os.path.join(config.result_path, f'{timestamp}.json')
        if not os.path.exists(config.result_path):
            os.makedirs(config.result_path)
        with open(result_json_dir, 'w') as f:
            json.dump(result_dict, f)


if __name__ == '__main__':
    config = Config(mode)
    if config.pretrained_model == "BERT-base":
        tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    elif config.pretrained_model == "ALBERT":
        from transformers import AlbertTokenizer
        tokenizer = AlbertTokenizer.from_pretrained('albert-base-v2')
    elif config.pretrained_model == "ROBERTA":
        from transformers import RobertaTokenizer
        tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    elif config.pretrained_model == "SciBERT":
        tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
    else:
        raise Exception("pretrained model not defined")
    # initialize data
    logger.info('Initializing data loader...')
    if mode == "ssh":
        train_dataloader = DataLoader(config.batch_size,
                                      data_file=config.processed_data + 'train.csv',
                                      tokenizer=tokenizer, max_seq_length=config.max_sequence_length, pretrained_model=config.pretrained_model)
        val_dataloader = DataLoader(config.batch_size, data_file=config.processed_data + 'test.csv',
                                    max_seq_length=config.max_sequence_length, is_test=True, tokenizer=tokenizer, pretrained_model = config.pretrained_model)
        logger.info('Initialized data loader .')
    else:
        train_dataloader = DataLoader(config.batch_size,
                                      data_file=config.processed_data + 'train.csv',
                                      tokenizer=tokenizer, max_seq_length=config.max_sequence_length, pretrained_model=config.pretrained_model)
        val_dataloader = DataLoader(config.batch_size, data_file=config.processed_data + 'test.csv',
                                    max_seq_length=config.max_sequence_length, is_test=True, tokenizer=tokenizer, pretrained_model = config.pretrained_model)
        logger.info('Initialized data loader .')
    train(train_dataloader=train_dataloader, valid_dataloader=val_dataloader)

