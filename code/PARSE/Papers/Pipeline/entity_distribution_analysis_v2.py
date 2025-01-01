import os
from rdflib import Graph, Namespace
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd

def analyze_ttl_file(file_path):
    """分析单个TTL文件中的实体类型及其频率"""
    g = Graph()
    g.parse(file_path, format="turtle")

    # 修改查询以直接获取实体类型
    query = """
    SELECT ?type
    WHERE {
        ?entity <https://www.anu.edu.au/onto/scholarly#entityType> ?type .
    }
    """

    type_counts = defaultdict(int)
    for row in g.query(query):
        type_str = str(row.type).strip('"@en')  # 处理可能的语言标签
        type_counts[type_str] += 1

    return dict(type_counts)

def analyze_all_files(directory):
    """分析目录中所有TTL文件"""
    file_type_counts = {}
    all_types = set()
    errors = []

    for filename in os.listdir(directory):
        if filename.endswith('.ttl'):
            file_path = os.path.join(directory, filename)
            try:
                type_counts = analyze_ttl_file(file_path)
                if type_counts:  # 只添加成功解析的文件
                    file_type_counts[filename] = type_counts
                    all_types.update(type_counts.keys())
            except Exception as e:
                errors.append(f"Error processing {filename}: {str(e)}")
                continue

    if not file_type_counts:
        raise ValueError("No files were successfully processed")

    # 打印错误信息但继续处理
    if errors:
        print("\nProcessing Errors:")
        for error in errors:
            print(error)

    # 转换为特征矩阵
    feature_matrix = []
    filenames = []
    for filename, counts in file_type_counts.items():
        features = [counts.get(type_, 0) for type_ in all_types]
        feature_matrix.append(features)
        filenames.append(filename)

    return np.array(feature_matrix), list(all_types), filenames

def create_cluster_visualization(feature_matrix, types, filenames, n_clusters=3):
    """创建改进的聚类可视化"""
    # 检查数据
    if len(filenames) < n_clusters:
        n_clusters = len(filenames)
        print(f"Reducing number of clusters to {n_clusters} due to small dataset size")

    # 标准化特征
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(feature_matrix)

    # K-means聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)

    # t-SNE降维
    perplexity = min(30, len(filenames)-1)
    tsne = TSNE(n_components=2, random_state=42, perplexity=max(5, perplexity))
    X_reduced = tsne.fit_transform(X_scaled)

    # 创建可视化
    plt.figure(figsize=(20, 10))

    # 1. 聚类散点图
    plt.subplot(1, 2, 1)

    # 为每个聚类使用不同的标记
    markers = ['o', 's', '^', 'D', 'v']
    for i in range(n_clusters):
        mask = clusters == i
        plt.scatter(X_reduced[mask, 0], X_reduced[mask, 1],
                    marker=markers[i % len(markers)],
                    label=f'Cluster {i}',
                    alpha=0.6, s=100)

    # 添加文件名标签（使用更好的标签布局）
    for i, (x, y) in enumerate(X_reduced):
        if i % max(1, len(filenames) // 20) == 0:  # 动态调整标签密度
            plt.annotate(filenames[i][:8] + '...',
                         (x, y),
                         xytext=(5, 5),
                         textcoords='offset points',
                         fontsize=8,
                         bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

    plt.title('File Clusters based on Entity Types')
    plt.legend()

    # 2. 特征重要性热图
    plt.subplot(1, 2, 2)

    # 计算每个聚类的特征重要性
    cluster_features = np.zeros((n_clusters, len(types)))
    for i in range(n_clusters):
        cluster_mask = clusters == i
        if np.any(cluster_mask):  # 确保该聚类有数据点
            cluster_features[i] = np.mean(X_scaled[cluster_mask], axis=0)

    # 选择最具区分性的特征
    feature_variance = np.var(cluster_features, axis=0)
    top_n = min(10, len(types))  # 确保不超过可用特征数量
    top_features_idx = np.argsort(feature_variance)[-top_n:]

    # 创建热图
    sns.heatmap(cluster_features[:, top_features_idx],
                xticklabels=[types[i] for i in top_features_idx],
                yticklabels=[f'Cluster {i}\n({np.sum(clusters == i)} files)'
                             for i in range(n_clusters)],
                cmap='coolwarm',
                center=0)

    plt.title('Cluster Characteristics\n(Normalized Feature Importance)')
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig('improved_clustering.png', bbox_inches='tight', dpi=300)
    plt.close()

    # 输出详细的聚类信息
    print("\nDetailed Cluster Analysis:")
    for i in range(n_clusters):
        cluster_mask = clusters == i
        cluster_size = np.sum(cluster_mask)
        print(f"\nCluster {i} ({cluster_size} files)")

        # 计算该聚类最具代表性的特征
        if cluster_size > 0:
            cluster_mean = np.mean(X_scaled[cluster_mask], axis=0)
            top_features = np.argsort(cluster_mean)[-5:]
            print("Most characteristic entity types:")
            for idx in reversed(top_features):
                print(f"  - {types[idx]}: {cluster_mean[idx]:.2f}")

def main():
    output_dir = 'output'

    print("Analyzing TTL files...")
    try:
        feature_matrix, types, filenames = analyze_all_files(output_dir)
        print(f"\nSuccessfully processed {len(filenames)} files")
        print(f"Found {len(types)} unique entity types")

        print("\nCreating visualization...")
        create_cluster_visualization(feature_matrix, types, filenames)

        print("\nAnalysis complete. Check 'improved_clustering.png' for visualization.")

    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    main()