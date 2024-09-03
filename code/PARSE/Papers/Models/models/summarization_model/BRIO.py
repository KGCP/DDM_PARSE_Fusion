"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 30/10/2022 9:04 pm
"""

from transformers import BartTokenizer, PegasusTokenizer
from transformers import BartForConditionalGeneration, PegasusForConditionalGeneration

IS_CNNDM = True # whether to use CNNDM dataset or XSum dataset
LOWER = False

with open("1711_07280_conclusion.txt") as f:
    ARTICLE_TO_SUMMARIZE = f.read()

# Load our model checkpoints
if IS_CNNDM:
    model = BartForConditionalGeneration.from_pretrained('Yale-LILY/brio-cnndm-uncased')
    tokenizer = BartTokenizer.from_pretrained('Yale-LILY/brio-cnndm-uncased')
else:
    model = PegasusForConditionalGeneration.from_pretrained('Yale-LILY/brio-xsum-cased')
    tokenizer = PegasusTokenizer.from_pretrained('Yale-LILY/brio-xsum-cased')

max_length = 1024 if IS_CNNDM else 512
# generation example
if LOWER:
    article = ARTICLE_TO_SUMMARIZE.lower()
else:
    article = ARTICLE_TO_SUMMARIZE
inputs = tokenizer([article], max_length=max_length, return_tensors="pt", truncation=True)
# Generate Summary
summary_ids = model.generate(inputs["input_ids"])
print(tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0])



