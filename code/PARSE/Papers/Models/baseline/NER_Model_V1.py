import torch.nn as nn
from torchcrf import CRF
from config import *
"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/24/2022 4:32 PM
"""

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        # word embedding
        self.embed = nn.Embedding(VOCAB_SIZE, EMBEDDING_DIM, WORD_PAD_ID)
        self.lstm = nn.LSTM(
            EMBEDDING_DIM,
            HIDDEN_SIZE,
            num_layers=NUM_LAYER,
            batch_first=True,
            bidirectional=True
        )
        self.linear = nn.Linear(2 * HIDDEN_SIZE, TARGET_SIZE)
        # instantiate CRF
        self.crf = CRF(TARGET_SIZE, batch_first=True)

    def _get_lstm_feature(self, input):
        out = self.embed(input)
        out, _ = self.lstm(out)
        return self.linear(out)

    # define forward process
    def forward(self, input, mask):
        out = self._get_lstm_feature(input)
        # use viterbi_decode to get our expected final result
        return self.crf.decode(out, mask)

    def loss_fn(self, input, target, mask):
        y_pred = self._get_lstm_feature(input)
        return -self.crf.forward(y_pred, target, mask, reduction='mean')
