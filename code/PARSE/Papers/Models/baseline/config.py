
"""
This is config file for NER PyTorch model
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/24/2022 5:58 PM
"""

# TRAIN_SAMPLE_DIR = "../models/dataset/train.csv"
# TEST_SAMPLE_DIR = "../models/dataset/test.csv"
TRAIN_SAMPLE_DIR = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/dataset/train.csv"
TEST_SAMPLE_DIR = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/dataset/test.csv"

VOCAB_PATH = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/baseline/output/vocab.txt"
LABEL_PATH = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/baseline/output/label.txt"


# fill the sentence, make each sentence length same
WORD_PAD = '<PAD>'
WORD_UNK = '<UNK>'

WORD_PAD_ID = 0
WORD_UNK_ID = 1

LABEL_O_ID = 0

# for OCR file, filter the wrong recognized words by set usual words numbers
VOCAB_SIZE = 25000

# word embedding vector dim
EMBEDDING_DIM = 300

HIDDEN_SIZE = 300
NUM_LAYER = 1
# output layer size: refer to label.txt
TARGET_SIZE = 15

# learning rate
LR = 1e-4
EPOCH = 30


MODEL_DIR = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/baseline/output"
RECORD_DIR = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/baseline/output/"

OPTIMIZER = "Adam"
# OPTIMIZER = "SGD"
# OPTIMIZER = "AdaDelta"
