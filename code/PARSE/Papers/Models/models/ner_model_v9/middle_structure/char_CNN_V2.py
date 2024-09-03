"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 1/5/2023 1:44 am
"""
import torch.nn as nn

class CharacterLevelCNN(nn.Module):
    def __init__(self, char_vocab_size, char_emb_dim, char_channels, char_kernel_size, num_chars):
        super(CharacterLevelCNN, self).__init__()
        self.char_embedding = nn.Embedding(char_vocab_size, char_emb_dim)
        self.num_chars = num_chars

        self.conv1 = nn.Sequential(
            nn.Conv1d(char_emb_dim, char_channels, kernel_size=char_kernel_size, padding=(char_kernel_size - 1) // 2),
            nn.ReLU(),
            nn.MaxPool1d(2 if num_chars >= 4 else 1)
        )

    def forward(self, input):
        input = self.char_embedding(input)
        batch_size, seq_length, num_chars, char_emb_dim = input.shape
        input = input.view(batch_size * seq_length, num_chars,
                           char_emb_dim)  # Merge batch_size and seq_length dimensions
        input = input.transpose(1,
                                2)  # Change from (batch_size * seq_length, num_chars, char_emb_dim) to (batch_size * seq_length, char_emb_dim, num_chars)
        output = self.conv1(input)

        output = output.view(batch_size, seq_length, -1)  # Restore batch_size and seq_length dimensions
        return output



