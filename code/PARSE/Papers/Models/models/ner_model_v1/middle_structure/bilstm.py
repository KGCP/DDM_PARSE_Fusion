import torch.nn as nn
import torch

"""
this is a bilistm network as utilities
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 8/15/2022 3:48 PM
"""


class bilstm(nn.Module):
    def __init__(self, embedding_dim, hidden_size, num_layers, tag_size, dropout_rate, is_layer_norm):
        super(bilstm, self).__init__()
        self.dropout = nn.Dropout(dropout_rate)
        self.bilstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_rate,
            bidirectional=True
        )

        self.is_layer_norm = is_layer_norm
        if is_layer_norm:
            self.layer_norm = nn.LayerNorm(hidden_size * 2)
        self.linear = nn.Linear(2 * hidden_size, tag_size)
        self.reset_params()

    def reset_params(self):
        nn.init.xavier_normal_(self.linear.weight)

    def get_lstm_features(self, mask, embedding):
        embedding = self.dropout(embedding)
        max_len, batch_size, embed_size = embedding.size()
        embedding = nn.utils.rnn.pack_padded_sequence(input=embedding, lengths=mask.sum(0).tolist(),
                                                      enforce_sorted=False)
        out, _ = self.bilstm(embedding)
        out, _ = nn.utils.rnn.pad_packed_sequence(out, total_length=max_len)
        out = out * mask.unsqueeze(-1)
        if self.is_layer_norm:
            out = self.layer_norm(out)
        lstm_features = self.linear(out) * mask.unsqueeze(-1)
        return lstm_features
