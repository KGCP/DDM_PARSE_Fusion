"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 28/4/2023 1:06 am
"""

from transformers import BertTokenizer

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

input_ids = [101, 1037, 2047, 4118, 2005, 15792, 5579, 1999, 3793, 26384, 1012, 102, 0, 0, 0, 0]

# Convert the token ids back to tokens
tokens = tokenizer.convert_ids_to_tokens(input_ids)

# Remove special tokens and padding tokens
filtered_tokens = [token for token in tokens if token not in ('[CLS]', '[SEP]', '[PAD]')]

# Join the tokens to form the original text
original_text = ' '.join(filtered_tokens)

print(original_text)
