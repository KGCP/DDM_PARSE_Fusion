"""
This is config file for NER model
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/24/2022 5:58 PM
"""
import os




class Config(object):

    def create_char2idx(self):
        char2idx = {char: idx for idx, char in enumerate(self.chars, 1)}
        char2idx['[PAD]'] = 0
        char2idx['[UNK]'] = len(char2idx)
        idx2char = {idx: char for char, idx in char2idx.items()}
        return char2idx, idx2char

    def __init__(self, mode):
        # this might be extended to other datatype, like finance and physics, etc.
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



        # global parameters
        self.seed = 2022
        self.batch_size = 8
        self.max_sequence_length = 100
        self.gpu = '0,1'
        self.train_from_ckpt = None
        self.pretrained_model = 'SciBERT' #ALBERT, ROBERTA, BERT-base, SciBERT, LinkBERT
        self.optimizer = "BertAdam"  # AdamW
        self.do_pgd = False
        self.general_learning_rate = 1e-4
        self.bert_learning_rate = 5e-5
        self.weight_decay_rate = 0.01
        self.patience = 4
        self.dropout_rate = 0.1
        self.decay_rate = 0.5
        self.mid_struct = 'bilstm' #idcnn, rtransformer, tener
        self.with_weight_layer = True

        # labels
        self.tags = ["[PAD]", "[CLS]", "[SEP]", "O",
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

        self.label_num = len(self.tags)

        self.chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-,;.!?:'\"/\\|_@#$%^&*~`+-=<>()[]{}"
        self.char2idx, self.idx2char = self.create_char2idx()
        self.char_vocab_size = len(self.char2idx)
        self.char_embed_size = 100
        self.max_word_length = 20

        # bilstm parameters
        self.bilstm_num_layers = 1
        self.lstm_hidden = 256
        self.gradient_accumulation_steps = 1
        self.train_epoch = 20
        self.warmup_proportion = 0.05
        self.vocab_size = 30522
        self.embedding_dim = 768
        self.is_layer_norm = True

        #CharCNN
        self.filters = 128
        self.kernel_size = 3
        self.num_chars = len(self.chars)

        # Tener
        self.num_layers = 1
        self.tener_hs = 256
        self.num_heads = 4
        # rTansformer
        self.k_size = 32
        self.rtrans_heads = 4

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
        elif self.pretrained_model == 'SciBERT':
            if mode == "ssh":
                self.model_dir = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/pre_trained_models/scibert"
            else:
                self.model_dir = '../pre_trained_models/scibert'
            self.pretrained_model_config = os.path.join(self.model_dir, 'config.json')
        elif self.pretrained_model == "LinkBERT":
            if mode == "ssh":
                self.model_dir = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/pre_trained_models/linkbert"
            else:
                self.model_dir = '../pre_trained_models/linkbert'
            self.pretrained_model_config = os.path.join(self.model_dir, 'config.json')
        else:
            raise Exception("model undefined")

