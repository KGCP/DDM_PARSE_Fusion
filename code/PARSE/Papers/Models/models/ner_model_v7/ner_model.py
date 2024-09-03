"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 8/15/2022 3:08 PM
"""

import os
import warnings
import torch
import torch.nn as nn
from transformers import BertConfig, BertPreTrainedModel, BertModel
from middle_structure import bilstm
from config import Config
from middle_structure.CRF import CRFLayer

mode = "ssh"
config = Config(mode)
warnings.filterwarnings('ignore')

class BertForNameEntityRecognition(BertPreTrainedModel):
    def __init__(self, bert_config):
        super().__init__(bert_config)
        self.label_size = config.label_num

        if config.pretrained_model in ['BERT-base', "ALBERT", "ROBERTA", "SciBERT", "DEBERTA"]:
            self.bert = BertModel(bert_config)
        else:
            raise Exception("pretrained model not defined")

        self.bilstm = bilstm(tag_size=self.label_size,
                             embedding_dim=bert_config.hidden_size,
                             hidden_size=config.lstm_hidden,
                             num_layers=config.bilstm_num_layers,
                             dropout_rate=config.dropout_rate,
                             is_layer_norm=True)

        self.output = nn.Linear(bert_config.hidden_size, self.label_size)
        self.crf = CRFLayer(config.label_num, config)

        self.init_weights()

        dym_weight_list = [bert_config.num_hidden_layers, 1, 1, 1]
        dym_weight_tensor = torch.ones(dym_weight_list)
        self.dym_weight = nn.Parameter(dym_weight_tensor, requires_grad=True)
        nn.init.xavier_normal_(self.dym_weight)

    def get_weight_layer(self, outputs):
        hidden_stack = torch.stack(outputs[1:], dim=0)
        sequence_output = torch.sum(hidden_stack * self.dym_weight,
                                    dim=0)
        return sequence_output

    def forward(
            self,
            input_ids=None,
            attention_mask=None,
            token_type_ids=None,
            labels=None,
    ):

        if config.pretrained_model in ["BERT-base", "ALBERT", "ROBERTA", "SciBERT", "DEBERTA"]:
            bert_output = self.bert(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
            )
            encoded_layers = bert_output.hidden_states
            sequence_output = bert_output.last_hidden_state
        else:
            raise Exception("pretrained model not defined")

        if config.with_weight_layer:
            sequence_output = self.get_weight_layer(encoded_layers)

        if config.mid_struct == 'bilstm':
            features = self.bilstm.get_lstm_features(embedding=sequence_output.transpose(1, 0), mask=attention_mask.transpose(1, 0))
        else:
            raise Exception("middle model not defined")

        if labels is not None:
            forward_score = self.crf(features, attention_mask.transpose(1, 0))
            score = self.crf.score_sentence(features, labels.transpose(1, 0),
                                            attention_mask.transpose(1, 0))
            loss = (forward_score - score).mean()
            return loss
        else:
            path = self.crf.viterbi_decode(features, attention_mask.transpose(1, 0))
            return path


if __name__ == '__main__':
    params = Config(mode)
    bert_config = BertConfig.from_json_file(os.path.join(config.pretrained_model_config))
    model = BertForNameEntityRecognition(bert_config)
    for n, p in model.named_parameters():
        print("the network structure is as follows:")
        print(n)
