"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 19/10/2022 4:34 pm
"""
from utils.calc_char_size import calc_char_size

class Data:

    def __init__(self):
        self.pretrain_word_embedding = None
        self.pretrain_char_embedding = None
        self.letter_size = calc_char_size()
        #prepare words
        self.word_alphabet = None
        self.feature_num = []
        feature_emb_dims = []
