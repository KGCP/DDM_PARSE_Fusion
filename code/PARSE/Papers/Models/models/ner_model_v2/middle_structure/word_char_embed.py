"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 19/10/2022 4:57 pm
"""

from __future__ import print_function
from __future__ import absolute_import
import torch
import torch.nn as nn
import numpy as np
from charCNN import CharCNN
from ..config import Config

config = Config()
#this is for initializing the word and letter embedding
class WordEmbed(nn.Module):

    def __init__(self, data):
        super(WordEmbed, self).__init__()

        self.gpu = config.with_gpu
        self.use_char = config.use_char
        self.batch_size = config.batch_size
        self.char_hidden_dim = 0
        self.char_all_feature = False

        if self.use_char:
            self.char_hidden_dim = config.char_hidden_dim
            self.char_embed_dim = config.char_embed_dim
            self.char_feature = CharCNN(data.pretrain_char_embedding, data.letter_size)

        self.word_embed_dim = config.word_embed_dim
        self.drop = nn.Dropout(config.dropout_rate)
        self.word_embedding = nn.Embedding(data.word_alphabet.size(), self.word_embed_dim)

        if data.pretrain_word_embedding is not None:
            self.word_embedding.weight.data.copy_(torch.from_numpy(data.pretrain_word_embedding))
        else:
            self.word_embedding.weight.data.copy_(torch.from_numpy(self.random_embedding(data.word_alphabet.size(), self.word_embed_dim)))

        self.feature_num = data.feature_num
        self.feature_embedding_dims = data.feature_emb_dims
        #ModuleList() this is a model containers for modules, like list[] or set()
        self.feature_embeddings = nn.ModuleList()

        for idx in range(self.feature_num):
            self.feature_embeddings.append(nn.Embedding(data.feature_alphabets[idx].size(), self.feature_embedding_dims[idx]))

        for idx in range(self.feature_num):
            if data.pretrain_feature_embeddings[idx] is not None:
                self.feature_embeddings[idx].weight.data.copy_(torch.from_numpy(data.pretrain_feature_embeddings[idx]))
            else:
                self.feature_embeddings[idx].weight.data.copy_(torch.from_numpy(self.random_embedding(data.feature_alphabets[idx].size(), self.feature_embedding_dims[idx])))

        if self.gpu:
            self.drop = self.drop.cuda()
            self.word_embedding = self.word_embedding.cuda()
            for idx in range(self.feature_num):
                self.feature_embeddings[idx] = self.feature_embeddings[idx].cuda()

    def random_embedding(self, vocab_size, embedding_dim):
        pretrain_emb = np.empty([vocab_size, embedding_dim])
        scale = np.sqrt(3.0 / embedding_dim)
        for index in range(vocab_size):
            pretrain_emb[index, :] = np.random.uniform(-scale, scale, [1, embedding_dim])
        return pretrain_emb

    def forward(self, word_inputs, feature_inputs, char_inputs, char_seq_recover):
        """
            input:
                word_inputs: (batch_size, sent_len)
                features: list [(batch_size, sent_len), (batch_len, sent_len),...]
                word_seq_lengths: list of batch_size, (batch_size,1)
                char_inputs: (batch_size*sent_len, word_length)
                char_seq_lengths: list of whole batch_size for char, (batch_size*sent_len, 1)
                char_seq_recover: variable which records the char order information, used to recover char order
            output:
                Variable(batch_size, sent_len, hidden_dim)
        """
        batch_size = word_inputs.size(0)
        sent_len = word_inputs.size(1)

        word_embs = self.word_embedding(word_inputs)

        word_list = [word_embs]

        for idx, embedding in enumerate(self.feature_embeddings):
            word_list.append(embedding(feature_inputs[idx]))

        if self.use_char:
            # calculate char lstm last hidden
            # print("charinput:", char_inputs)
            # exit(0)
            char_features = self.char_feature(char_inputs)
            char_features = char_features[char_seq_recover]
            char_features = char_features.view(batch_size, sent_len, -1)

            # concat word and char together
            word_list.append(char_features)
            word_embs = torch.cat([word_embs, char_features], 2)

            if not torch.jit.is_scripting():
                if self.char_all_feature:
                    char_features_extra = self.char_feature_extra.get_last_hiddens(char_inputs)
                    char_features_extra = char_features_extra[char_seq_recover]
                    char_features_extra = char_features_extra.view(batch_size, sent_len, -1)
                    # concat word and char together
                    word_list.append(char_features_extra)

        word_embs = torch.cat(word_list, 2)
        word_represent = self.drop(word_embs)

        return word_represent
