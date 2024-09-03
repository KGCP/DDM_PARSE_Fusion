
"""
This is config file for NER model
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/24/2022 5:58 PM
"""
import json
import os
class Config(object):
    def __init__(self, mode):
        # Set all the parameters directly
        if mode == 'ssh':
            self.processed_data = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/dataset/"
            self.save_model = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/saved_model/"
            self.save_ckpt_path = ""
            self.result_path = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/result/"
            self.predict_dict_output_path = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/predict_result/"
            self.predict_text_output_path = self.predict_dict_output_path
            self.predict_input_path = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/dataset/askg/"
            self.predict_model_path = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/trained_model/model_0.6437_0.7174_0.6761_810.bin"
        else:
            self.processed_data = "../dataset/"
            self.save_model = "./saved_model/"
            self.save_ckpt_path = ""
            self.result_path = "./result/"
            self.predict_dict_output_path = "./predict_result"
            self.predict_text_output_path = self.predict_dict_output_path
            self.predict_input_path = "./dataset/askg"
            self.predict_model_path = "./trained_model/model_0.6437_0.7174_0.6761_810.bin"
        self.with_bert = False
        self.train_epoch = 30
        self.seed = 2023
        self.batch_size = 32
        self.char_hidden_dim = 50
        self.char_embed_dim = 30
        self.use_char = True
        self.word_embed_dim = 512
        self.cnn_layer = 4
        self.with_gpu = True
        self.gpu = "0,1"
        self.train_from_ckpt = None
        self.max_sentence_length = 512
        self.max_sequence_length = 32
        self.max_word_length = -1
        self.pretrained_model = "ROBERTA" #OAG_BERT, ALBERT, ROBERTA, BERT-base
        self.char_feature_extractor = "CNN"
        self.optimizer = "AdamW"
        self.do_pgd = False
        self.general_learning_rate = 5e-3
        self.bert_learning_rate = 5e-5
        self.weight_decay_rate = 0.05
        self.patience = 4
        self.dropout_rate = 0.1
        self.decay_rate = 0.1
        self.l2_rate = 1e-8
        self.mid_struct = "bilstm"
        self.with_weight_layer = False
        self.gradient_accumulation_steps = 1
        self.warmup_proportion = 0.05
        self.is_save = True
        self.tag_class = [
            "SOLUTION",
            "RESEARCH_PROBLEM",
            "METHOD",
            "DATASET",
            "TOOL",
            "LANGUAGE",
            "RESOURCE"
        ]
        self.tags = [
            "[PAD]", "[CLS]", "[SEP]", "O",
            "I-SOLUTION",
            "I-RESEARCH_PROBLEM",
            "B-SOLUTION",
            "B-RESEARCH_PROBLEM",
            "I-RESOURCE",
            "I-METHOD",
            "B-METHOD",
            "B-RESOURCE",
            "I-DATASET",
            "I-TOOL",
            "B-TOOL",
            "B-LANGUAGE",
            "B-DATASET",
            "I-LANGUAGE",
        ]

        # self.tags = [
        #     "[PAD]", "[CLS]", "[SEP]", "O",
        #     "I-SOLUTION",
        #     "I-RESEARCH_PROBLEM",
        #     "B-SOLUTION",
        #     "B-RESEARCH_PROBLEM",
        #     "I-RESOURCE",
        #     "I-METHOD",
        #     "B-METHOD",
        #     "B-RESOURCE",
        #     "I-DATASET",
        #     "I-TOOL",
        #     "B-TOOL",
        #     "B-LANGUAGE",
        #     "B-DATASET",
        #     "I-LANGUAGE",
        #     "S-SOLUTION",
        #     "S-RESEARCH_PROBLEM",
        #     "S-METHOD",
        #     "S-DATASET",
        #     "S-TOOL",
        #     "S-LANGUAGE",
        #     "S-RESOURCE",
        #     "E-SOLUTION",
        #     "E-RESEARCH_PROBLEM",
        #     "E-METHOD",
        #     "E-DATASET",
        #     "E-TOOL",
        #     "E-LANGUAGE",
        #     "E-RESOURCE"
        # ]
        self.label_num = len(self.tags)
        self.bilstm_layers = 2
        self.bilstm_hidden_dim = 768
        self.k_size = 32
        self.rtrans_heads = 4
        self.NEL_input_path = "../predict_result/test_dict.json"
        self.mode = "all"
        self.remove_stopwords = True
        self.try_lemmatize = True
        self.min_length = 2
        self.max_length = 4

        if self.pretrained_model == 'BERT-base':
            if mode == "ssh":
                self.model_dir = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/pre_trained_models/bert-base-uncased"
            else:
                self.model_dir = '../pre_trained_models/bert-base-uncased'
            self.pretrained_model_config = os.path.join(self.model_dir, 'config.json')
        elif self.pretrained_model == 'ALBERT':
            if mode == "ssh":
                self.model_dir = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/pre_trained_models/albert"
            else:
                self.model_dir = '../pre_trained_models/albert'
            self.pretrained_model_config = os.path.join(self.model_dir, 'config.json')
        elif self.pretrained_model == 'ROBERTA':
            if mode == "ssh":
                self.model_dir = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/pre_trained_models/roberta"
            else:
                self.model_dir = '../pre_trained_models/roberta'
            self.pretrained_model_config = os.path.join(self.model_dir, 'config.json')
        elif self.pretrained_model == 'OAG_BERT':
            pass
        else:
            raise Exception("model undefined")








