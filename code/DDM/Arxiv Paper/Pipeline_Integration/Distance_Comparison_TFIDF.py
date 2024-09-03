from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 替换这里的文本为你的目标文本
text1 = "这是第一段文本的内容。"
text2 = "这是第二段文本的内容，可能与第一段相似或不同。"

# 将文本放入一个列表中，便于向量化
texts = [text1, text2]

# 初始化TF-IDF向量化器
vectorizer = TfidfVectorizer()

# 将文本转换为TF-IDF特征向量
tfidf_matrix = vectorizer.fit_transform(texts)

# 计算两个特征向量的余弦相似度
cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

print(f"两段文本的余弦相似度为: {cosine_sim[0][0]}")
