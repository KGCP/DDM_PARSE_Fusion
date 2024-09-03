
"""
This is config file for NER model
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/24/2022 5:58 PM
"""
import json
import os

class Config(object):
    def __init__(self):
        # load config from json file
        config_path = "config.json"
        config_dict = {}
        with open(config_path, 'r') as f:
            config_dict = json.load(f)

        # this might be extended to other datatype, like finance and physics, etc.
        self.data_type = 'computer_science'
        if self.data_type == 'computer_science':
            # path
            self.processed_data = config_dict["processed_data"]
            self.saved_model = config_dict["saved_model"]
            self.save_model = config_dict["save_model"]
            self.tag_path = config_dict["tag_path"]
            self.save_ckpt_path = config_dict["save_ckpt_path"]
            self.model_dir = config_dict["model_dir"]
            self.result_path = config_dict["result_path"]
            self.predict_model_path = config_dict["predict_model_path"]
            self.tag_class = config_dict["tag_class"]

            # global parameters
            self.train_epoch = config_dict["train_epoch"]
            self.seed = config_dict["seed"]
            self.batch_size = config_dict["batch_size"]
            self.max_sequence_length = config_dict["max_sequence_length"]
            self.gpu = config_dict["gpu"]
            self.train_from_ckpt = None if config_dict["train_from_ckpt"] == "" else config_dict
            self.pretrained_model = config_dict["pretrained_model"] #bert, roberta, deberta
            self.optimizer = config_dict["optimizer"]  # AdamW, BertAdam
            self.do_pgd = config_dict["do_pgd"]
            self.general_learning_rate = config_dict["general_learning_rate"]
            self.bert_learning_rate = config_dict["bert_learning_rate"]
            self.weight_decay_rate = config_dict["weight_decay_rate"]
            self.patience = config_dict["patience"]
            self.dropout_rate = config_dict["dropout_rate"]
            self.decay_rate = config_dict["decay_rate"]
            self.mid_struct = config_dict["mid_struct"]  # rtransformer
            self.with_weight_layer = config_dict["with_weight_layer"]
            self.gradient_accumulation_steps = config_dict["gradient_accumulation_steps"]
            self.warmup_proportion = config_dict["warmup_proportion"]
            self.is_save = config_dict["is_save"]
            self.predict_dict_output_path = config_dict["predict_dict_output_path"]
            self.predict_text_output_path = config_dict["predict_text_output_path"]

            # labels
            self.tags = config_dict["tags"]
        self.label_num = len(self.tags)

        # bilstm parameters
        self.bilstm_num_layers = config_dict["bilstm_num_layers"]
        self.lstm_hidden = config_dict["lstm_hidden"]
        # Rtransformer parameters
        self.k_size = config_dict["k_size"]
        self.rtrans_heads = config_dict["rtrans_heads"]


        if self.pretrained_model == 'bert':
            self.model_dir = '../pre_trained_models/bert-base-uncased'
        elif self.pretrained_model == 'xlm_roberta':
            self.model_dir = '../pre_trained_models/xlm_roberta'
        elif self.pretrained_model == 'roberta':
            self.model_dir = '../pre_trained_models/roberta'
        elif self.pretrained_model == 'deberta':
            self.model_dir = '../pre_trained_models/deberta'
        else:
            raise Exception("model undefined")

        if self.pretrained_model == "bert":
            self.pretrained_model_config = os.path.join(self.model_dir)
        elif self.pretrained_model == 'xlm_roberta':
            self.pretrained_model_config = os.path.join(self.model_dir, 'config.json')
        elif self.pretrained_model == 'roberta':
            self.pretrained_model_config = os.path.join(self.model_dir, 'config.json')
        elif self.pretrained_model == 'deberta':
            self.pretrained_model_config = os.path.join(self.model_dir)
        else:
            raise Exception("pretrained model config not defined")

if __name__ == '__main__':
    c = Config()









