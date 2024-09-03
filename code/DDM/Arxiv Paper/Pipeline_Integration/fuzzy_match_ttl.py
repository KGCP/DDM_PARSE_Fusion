from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 加载TTL文件
ttl_file_path = 'C:/Users/6/Desktop/Arxiv/Experiment/IntegratedTTL/ASKG_Integrated_10.ttl'
g = Graph()
g.parse(ttl_file_path, format="ttl")

# 定义命名空间
ASKG_ONTO = URIRef("https://www.anu.edu.au/onto/scholarly#")

# Extract Excerpt and Paragraph text
excerpts_texts = [str(o) for s, p, o in g if 'inSentence' in str(p)]
paragraphs_texts = [str(o) for s, p, o in g if 'label' in str(p) and 'Paragraph' in str(s)]

# Use TF-IDF vectorized text
vectorizer = TfidfVectorizer()
all_texts = excerpts_texts + paragraphs_texts  # 将摘录和段落文本合并
tfidf_matrix = vectorizer.fit_transform(all_texts)

# Calculate the cosine similarity between the excerpt and the paragraph
excerpts_matrix = tfidf_matrix[:len(excerpts_texts)]
paragraphs_matrix = tfidf_matrix[len(excerpts_texts):]
cos_sim_matrix = cosine_similarity(excerpts_matrix, paragraphs_matrix)

# 确定匹配阈值
threshold = 0.3  # 可以调整这个阈值

# 统计匹配的数量
matched_excerpts_count = sum(np.max(cos_sim_matrix, axis=1) > threshold)

# 输出结果
print(f"Total excerpts: {len(excerpts_texts)}")
print(f"Excerpts matched with a paragraph (similarity > {threshold}): {matched_excerpts_count}")
