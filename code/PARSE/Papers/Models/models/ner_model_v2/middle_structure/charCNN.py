"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 20/9/2022 2:09 am
"""

# -*- coding: utf-8 -*-
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from ..config import Config

config = Config()
class CharCNN(nn.Module):
    def __init__(self, pretrain_char_embedding, alphabet_size):
        super(CharCNN, self).__init__()

        self.gpu = config.with_gpu
        self.hidden_dim = config.char_hidden_dim
        self.char_drop = nn.Dropout(config.dropout_rate)
        self.alphabet_size = alphabet_size
        self.char_embed_dim = config.char_embed_dim
        self.char_embeddings = nn.Embedding(self.alphabet_size, self.char_embed_dim)

        # assign pre-trained char weight for the embedding layer
        if pretrain_char_embedding is not None:
            self.char_embeddings.weight.data.copy_(torch.from_numpy(pretrain_char_embedding))
        else:
            self.char_embeddings.weight.data.copy_(torch.from_numpy(self.random_embedding(self.alphabet_size, self.char_embed_dim)))

        # use dim-1 convolution network
        self.char_cnn = nn.Conv1d(self.char_embed_dim, self.hidden_dim, kernel_size=3, padding=1)
        if self.gpu:
            self.char_drop = self.char_drop.cuda()
            self.char_embeddings = self.char_embeddings.cuda()
            self.char_cnn = self.char_cnn.cuda()

    def random_embedding(self, vocab_size, char_embed_dim):
        pretrain_emb = np.empty([vocab_size, char_embed_dim])
        scale = np.sqrt(3.0 / char_embed_dim)
        for index in range(vocab_size):
            # initialize each letter's embedding tensor
            pretrain_emb[index, :] = np.random.uniform(-scale, scale, [1, char_embed_dim])
        return pretrain_emb

    def forward(self, input):
        """
            input:
                input: Variable(batch_size, word_length)
                seq_lengths: numpy array (batch_size,  1)
            output:
                Variable(batch_size, char_hidden_dim)
            Note it only accepts ordered (length) variable, length size is recorded in seq_lengths
        """
        batch_size = input.size(0)
        char_embeds = self.char_drop(self.char_embeddings(input))
        char_embeds = char_embeds.transpose(2, 1).contiguous()
        char_cnn_out = self.char_cnn(char_embeds)
        char_cnn_out = F.max_pool1d(char_cnn_out, char_cnn_out.size(2)).view(batch_size, -1)
        return char_cnn_out

