from transformers import AutoModel, AutoTokenizer
import torch
from rdflib import Graph, Namespace, URIRef, Literal
import numpy as np

# 加载模型和分词器
model_name = "avsolatorio/GIST-Embedding-v0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# 定义文本嵌入函数
def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state[:, 0, :]
    return embeddings

# 加载TTL文件
ttl_file_path = 'C:/Users/6/Desktop/ASKG.ttl'
g = Graph()
g.parse(ttl_file_path, format="ttl")

# 定义命名空间
ASKG_ONTO = Namespace("https://www.anu.edu.au/onto/scholarly#")

# 提取Excerpt和Paragraph文本及其URI
excerpts = [(str(o), s) for s, p, o in g if 'inSentence' in str(p)]
paragraphs = [(str(o), s) for s, p, o in g if 'label' in str(p) and 'Paragraph' in str(s)]

# 获取摘录和段落的嵌入
excerpts_embeddings = torch.cat([get_embedding(text) for text, _ in excerpts])
paragraphs_embeddings = torch.cat([get_embedding(text) for text, _ in paragraphs])

# 计算余弦相似度
cos_sim_matrix = torch.nn.functional.cosine_similarity(excerpts_embeddings[:, None, :], paragraphs_embeddings[None, :, :], dim=2)

# 确定匹配阈值
threshold = 0.7

# 找出每个摘录匹配的段落（最高相似度且超过阈值）
matches = []
for excerpt_idx, sim_scores in enumerate(cos_sim_matrix):
    paragraph_idx = sim_scores.argmax().item()
    if sim_scores[paragraph_idx] > threshold:
        matches.append((excerpts[excerpt_idx][1], paragraphs[paragraph_idx][1]))  # (excerpt_uri, paragraph_uri)

# 定义新的关系URI
hasExcerpt = ASKG_ONTO.hasExcerpt

# 为匹配的摘录和段落添加新的关系
for excerpt_uri, paragraph_uri in matches:
    g.add((paragraph_uri, hasExcerpt, excerpt_uri))

# 输出结果
print(f"Total excerpts: {len(excerpts)}")
print(f"Excerpts matched with a paragraph (similarity > {threshold}): {len(matches)}")

# 如果你需要将更新后的图导出到文件
output_ttl_path = 'C:/Users/6/Desktop/Arxiv/Experiment/IntegratedTTL/ASKG_Integrated_10_updated.ttl'
g.serialize(destination=output_ttl_path, format='turtle')
