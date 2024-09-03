"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 26/4/2023 10:48 am
"""

import torch
from transformers import BertTokenizer, BertForTokenClassification


def entity_disambiguation(text, model_name='bert-base-chinese'):
    # 加载预训练模型和分词器
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertForTokenClassification.from_pretrained(model_name)

    # 对输入文本进行编码
    inputs = tokenizer(text, return_tensors='pt')

    # 获取模型输出
    outputs = model(**inputs)
    predictions = torch.argmax(outputs.logits, dim=2)

    # 获取实体标签
    id2label = model.global_config.id2label
    labels = [id2label[prediction] for prediction in predictions[0].tolist()]

    # 格式化输出结果
    tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
    result = [(token, label) for token, label in zip(tokens, labels)]

    return result


# 示例输入
text = "上海市和北京市是中国的两个直辖市。"

# 实体消歧
result = entity_disambiguation(text)
print(result)
