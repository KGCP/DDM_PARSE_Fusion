def compute_jaccard_distance(set1, set2):
    """
    计算两个集合之间的Jaccard Distance。

    :param set1: 第一个实体集合。
    :param set2: 第二个实体集合。
    :return: Jaccard Distance。
    """
    # 计算交集和并集
    intersection = set1.intersection(set2)
    union = set1.union(set2)

    # 计算Jaccard Distance
    jaccard_distance = 1 - len(intersection) / len(union)
    return jaccard_distance


# 定义两组实体的唯一集合
entities_group_1 = set([
    "named entity recognition (NER)",
    "deep learning techniques",
    "recurrent neural networks (RNNs)",
    "transformers",
    "natural language processing (NLP)",
    "sentiment analysis",
    "information extraction",
    "multilingual and cross-lingual NER",
    "text data",
    "names",
    "locations",
    "organizations",
    "relationships and events"
])



entities_group_2 = set([
    "named entity recognition",
    "deep learning techniques",
    "recurrent neural networks",
    "convolutional neural networks",
    "transfer learning",
    "pre-trained models",
    "multimodal named entity recognition",
    "text",
    "images",
    "audio",
    "information extraction",
    "names",
    "locations",
    "organizations",
    "sentiment analysis",
    "summary generation"
])





# 计算并输出Jaccard Distance
jaccard_distance = compute_jaccard_distance(entities_group_1, entities_group_2)
print(f"Jaccard Distance: {jaccard_distance}")
