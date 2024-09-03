# import torch
# from transformers import BertTokenizer, BertForMaskedLM
#
# # 加载预训练的OAGBERT模型和分词器
# model_name = "bert-base-uncased"
# tokenizer = BertTokenizer.from_pretrained(model_name)
# model = BertForMaskedLM.from_pretrained(model_name)
#
#
# # 定义一个用于实体消歧义的函数
# def disambiguate_entity(context, ambiguous_entity, candidate_entities):
#     max_score = float('-inf')
#     best_entity = None
#
#     for entity in candidate_entities:
#         # 将实体插入到上下文中
#         text = context.replace('<ambiguous_entity>', entity)
#
#         # 对上下文进行分词
#         inputs = tokenizer(text, return_tensors="pt")
#
#         # 使用模型进行预测
#         with torch.no_grad():
#             outputs = model(**inputs)
#             predictions = outputs.logits
#
#         # 计算预测分数
#         score = torch.mean(predictions).item()
#
#         # 选择最佳实体
#         if score > max_score:
#             max_score = score
#             best_entity = entity
#
#     return best_entity
#
#
# # 示例：实体消歧义
# context = "<ambiguous_entity> field of computer science and linguistics。"
# ambiguous_entity = "<ambiguous_entity>"
# candidate_entities = ["Natrual Language Processing", "neuro-linguistic programming"]
#
# result = disambiguate_entity(context, ambiguous_entity, candidate_entities)
# print("消歧后的实体：", result)

from transformers import BertModel, BertTokenizer
import torch

def predict_link_relation(doc1, doc2, model, tokenizer):
    sentence1 = doc1
    sentence2 = doc2
    inputs = tokenizer([sentence1, sentence2], return_tensors='pt', padding=True, truncation=True)

    # 使用BERT编码器编码两个句子，并提取[CLS]向量作为句子表示
    outputs = model(**inputs)
    cls_vectors = outputs.last_hidden_state[:, 0, :]

    # 定义一个二分类器，用于预测sentence2是否是sentence1的下一句
    classifier = torch.nn.Sequential(
        torch.nn.Linear(768, 256),
        torch.nn.ReLU(),
        torch.nn.Linear(256, 2),
        torch.nn.Softmax(dim=1)
    )

    # 预测句子2是否是句子1的下一句
    probs = classifier(cls_vectors)
    is_next = torch.argmax(probs, dim=1).item()

    if is_next == 1:
        print("Sentence 2 is the next sentence of Sentence 1.")
    else:
        print("Sentence 2 is not the next sentence of Sentence 1.")


if __name__ == "__main__":
    model_name = "michiyasunaga/LinkBERT-base"
    model = BertModel.from_pretrained(model_name)
    tokenizer = BertTokenizer.from_pretrained(model_name)

    doc1 = "Full network pre-training (Dai & Le, 2015; Radford et al., 2018; Devlin et al., 2019; Howard & Ruder, 2018) has led to a series of breakthroughs in language representation learning. Many nontrivial NLP tasks, including those that have limited training data, have greatly benefited from these pre-trained models. One of the most compelling signs of these breakthroughs is the evolution of machine performance on a reading comprehension task designed for middle and high-school English exams in China, the RACE test (Lai et al., 2017): the paper that originally describes the task and formulates the modeling challenge reports then state-of-the-art machine accuracy at 44.1%; the latest published result reports their model performance at 83.2% (Liu et al., 2019); the work we present here pushes it even higher to 89.4%, a stunning 45.3% improvement that is mainl"

    #similar or same paper to doc1
    doc2 = "Evidence from these improvements reveals that a large network is of crucial importance for achieving state-of-the-art performance (Devlin et al., 2019; Radford et al., 2019). It has become common practice to pre-train large models and distill them down to smaller ones (Sun et al., 2019; Turc et al., 2019) for real applications. Given the importance of model size, we ask: Is having better NLP models as easy as having larger models?"
    #doc2 = "ALBERT incorporates two parameter reduction techniques that lift the major obstacles in scaling pre-trained models. The first one is a factorized embedding parameterization. By decomposing the large vocabulary embedding matrix into two small matrices, we separate the size of the hidden layers from the size of vocabulary embedding. This separation makes it easier to grow the hidden size without significantly increasing the parameter size of the vocabulary embeddings. The second technique is cross-layer parameter sharing. This"
    #doc2 = "As a result of these design decisions, we are able to scale up to much larger ALBERT configurations that still have fewer parameters than BERT-large but achieve significantly better performance. We establish new state-of-the-art results on the well-known GLUE, SQuAD, and RACE benchmarks for natural language understanding. Specifically, we push the RACE accuracy to 89.4%, the GLUE benchmark to 89.4, and the F1 score of SQuAD 2.0 to 92.2."

    #Not related paper to doc1
    #doc2 = "canonical models are of central importance in modal logic. This paper presents a generic canonical model construction in the semantic framework of coalgebraic modal"
    #doc2 = "We use a random coding scheme with a drop-when-decoded rule for queue update. We assume that each slot is served independently of the others. We also assume that the queue update rule can track the size of the virtual queue. The algorithm is based on Bernoulli arrival and receipt times."

    predict_link_relation(doc1, doc2, model, tokenizer)