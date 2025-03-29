import os
from rdflib import Graph, Namespace
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd

def analyze_ttl_file(file_path):
    g = Graph()
    g.parse(file_path, format="turtle")

    askg_onto = Namespace("https://www.anu.edu.au/onto/scholarly#")

    entity_types = []
    query = """
    SELECT DISTINCT ?label ?type
    WHERE {
        ?entity <http://www.w3.org/2000/01/rdf-schema#label> ?label ;
                <https://www.anu.edu.au/onto/scholarly#entityType> ?type .
        FILTER(str(?type) != "Concept@en" && str(?type) != "Concept")
    }
    """

    for row in g.query(query):
        entity_type = str(row.type)
        if '@' in entity_type:
            entity_type = entity_type.split('@')[0]
        entity_types.append(entity_type)

    return entity_types

def analyze_all_files(directory):
    """分析目录中所有TTL文件"""
    all_entity_types = []
    file_entity_types = {}

    for filename in os.listdir(directory):
        if filename.endswith('.ttl'):
            file_path = os.path.join(directory, filename)
            try:
                entity_types = analyze_ttl_file(file_path)
                all_entity_types.extend(entity_types)
                file_entity_types[filename] = entity_types
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return all_entity_types, file_entity_types

def visualize_distribution(all_entity_types):
    """可视化实体类型分布"""
    counter = Counter(all_entity_types)

    plt.figure(figsize=(12, 6))
    plt.bar(counter.keys(), counter.values())
    plt.xticks(rotation=45, ha='right')
    plt.title('Distribution of Entity Types')
    plt.xlabel('Entity Type')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig('entity_type_distribution.png')
    plt.close()

def cluster_files(file_entity_types):
    """对文件进行聚类分析"""
    # 准备数据
    file_names = list(file_entity_types.keys())
    entity_lists = [' '.join(types) for types in file_entity_types.values()]

    # TF-IDF向量化
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(entity_lists)

    # K-means聚类
    n_clusters = min(3, len(file_names))  # 设置聚类数
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X)

    # 使用t-SNE降维可视化
    from sklearn.manifold import TSNE
    tsne = TSNE(n_components=2, random_state=42)
    X_reduced = tsne.fit_transform(X.toarray())

    # 可视化聚类结果
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=clusters, cmap='viridis')
    plt.title('Clustering of Files based on Entity Types')

    # 添加文件名标签
    for i, txt in enumerate(file_names):
        plt.annotate(txt, (X_reduced[i, 0], X_reduced[i, 1]), fontsize=8)

    plt.colorbar(scatter)
    plt.tight_layout()
    plt.savefig('file_clusters.png')
    plt.close()

def main():
    # 设置输出目录
    output_dir = 'output'

    # 分析所有文件
    print("Analyzing TTL files...")
    all_entity_types, file_entity_types = analyze_all_files(output_dir)

    # 打印统计信息
    print("\nEntity Type Distribution:")
    counter = Counter(all_entity_types)
    for entity_type, count in counter.most_common():
        print(f"{entity_type}: {count}")

    # 生成可视化
    print("\nGenerating visualizations...")
    visualize_distribution(all_entity_types)
    cluster_files(file_entity_types)

    print("\nAnalysis complete. Check 'entity_type_distribution.png' and 'file_clusters.png' for visualizations.")

if __name__ == "__main__":
    main()