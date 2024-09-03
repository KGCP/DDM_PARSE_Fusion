"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 19/10/2022 6:47 pm
"""

from __future__ import print_function
from __future__ import absolute_import
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
from word_char_embed import WordEmbed
from ..config import Config

config = Config()
# this is the model structure (sequence -> word_char_embed -> charCNN)
class Sequence(nn.Module):

    def __init__(self, data):
        super(Sequence, self).__init__()

        self.gpu = config.with_gpu
        self.use_char = config.use_char
        self.droplstm = nn.Dropout(config.dropout_rate)
        self.bilstm_flag = True if config.mid_struct == "bilstm" else False
        self.lstm_layer = config.bilstm_layers
        self.word_embed = WordEmbed(data)
        self.input_size = config.word_embed_dim
        self.feature_num = data.feature_num

        if self.use_char:
            self.input_size = self.input_size + config.char_hidden_dim
            if data.char_feature_extractor == "ALL":
                self.input_size = self.input_size + config.char_hidden_dim

        for idx in range(self.feature_num):
            self.input_size = self.input_size + data.feature_emb_dims[idx]

        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        if self.bilstm_flag:
            lstm_hidden = config.lstm_hidden_dim // 2
        else:
            lstm_hidden = config.lstm_hidden_dim

        if config.mid_struct == "bilstm":
            self.lstm = nn.LSTM(self.input_size, lstm_hidden, num_layers=self.lstm_layer, batch_first=True,
                                bidirectional=self.bilstm_flag)

        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(config.lstm_hidden_dim, config.label_num)

    def forward(self, word_inputs, feature_inputs, word_seq_lengths, char_inputs, char_seq_recover):
        """
            input:
                word_inputs: (batch_size, sent_len)
                feature_inputs: [(batch_size, sent_len), ...] list of variables
                word_seq_lengths: list of batch_size, (batch_size,1)
                char_inputs: (batch_size*sent_len, word_length)
                char_seq_lengths: list of whole batch_size for char, (batch_size*sent_len, 1)
                char_seq_recover: variable which records the char order information, used to recover char order
            output:
                Variable(batch_size, sent_len, hidden_dim)
        """

        word_represent = self.word_embed(word_inputs, feature_inputs, char_inputs, char_seq_recover)

        # word_embs (batch_size, seq_len, embed_size)
        if not torch.jit.is_scripting():
            if self.word_feature_extractor == "CNN":
                batch_size = word_inputs.size(0)
                word_in = torch.tanh(self.word2cnn(word_represent)).transpose(2, 1).contiguous()

                for idx in range(self.cnn_layer):
                    if idx == 0:
                        cnn_feature = F.relu(self.cnn_list[idx](word_in))
                    else:
                        cnn_feature = F.relu(self.cnn_list[idx](cnn_feature))
                    cnn_feature = self.cnn_drop_list[idx](cnn_feature)
                    if batch_size > 1:
                        cnn_feature = self.cnn_batchnorm_list[idx](cnn_feature)
                feature_out = cnn_feature.transpose(2, 1).contiguous()
            else:
                packed_words = pack_padded_sequence(word_represent, word_seq_lengths.cpu().numpy(), True)
                hidden = None
                lstm_out, hidden = self.lstm(packed_words, hidden)
                lstm_out, _ = pad_packed_sequence(lstm_out)
                # lstm_out (seq_len, seq_len, hidden_size)
                feature_out = self.droplstm(lstm_out.transpose(1, 0))

        elif torch.jit.is_scripting():
            packed_words = pack_padded_sequence(word_represent, word_seq_lengths.cpu(), True)
            hidden = None
            lstm_out, hidden = self.lstm(packed_words, hidden)
            lstm_out, _ = pad_packed_sequence(lstm_out)
            # lstm_out (seq_len, seq_len, hidden_size)
            feature_out = self.droplstm(lstm_out.transpose(1, 0))

        # feature_out (batch_size, seq_len, hidden_size)
        outputs = self.hidden2tag(feature_out)
        return outputs
