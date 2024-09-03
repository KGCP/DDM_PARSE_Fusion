"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 3/4/2023 1:26 am
"""
import re

import numpy as np
from rdflib import Graph, Namespace, RDFS
from rdflib.plugins.sparql import prepareQuery
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import matplotlib.pyplot as plt

def getKeyword():

    g = Graph()
    g.parse("ASKG.ttl", format="turtle")

    query = prepareQuery("""
        PREFIX askg: <https://www.anu.edu.au/onto/scholarly#>

        SELECT ?keyword (COUNT(?keywordInstance) AS ?frequency)
        WHERE {
        ?keyword a askg:Keyword .
        ?keywordInstance askg:correspondsTo ?keyword .
        }
        GROUP BY ?keyword
        ORDER BY DESC(?frequency)
        LIMIT 40
        """)

    keywords = []
    for row in g.query(query):
        keyword_part = row.keyword.split("#Keyword-")[-1].replace("_", " ")
        pattern = r"(-Q\d+)$"
        result = re.sub(pattern, "", keyword_part)
        keywords.append(result)

    print(keywords)
    return keywords

if __name__ == "__main__":
    g = Graph()
    g.parse("ASKG.ttl", format="turtle")

    ASKG = Namespace("https://www.anu.edu.au/onto/scholarly#")
    keywords = getKeyword()

    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModel.from_pretrained("bert-base-uncased")

    embeddings = []

    for keyword in keywords:
        inputs = tokenizer(keyword, return_tensors="pt")
        outputs = model(**inputs)
        embeddings.append(outputs[0][:, 0, :].detach().numpy())

    embeddings = np.vstack(embeddings)

    similarity_matrix = cosine_similarity(embeddings)

    G = nx.Graph()
    G.add_nodes_from(keywords)

    similarity_threshold = 0.9

    for i, keyword1 in enumerate(keywords):
        for j, keyword2 in enumerate(keywords):
            if i != j and similarity_matrix[i][j] > similarity_threshold:
                G.add_edge(keyword1, keyword2, weight=similarity_matrix[i][j])

    k = 1.3
    pos = nx.spring_layout(G, seed=42, k = k)
    plt.figure(figsize=(20, 20))

    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=12, font_weight="bold", alpha=0.8)
    plt.show()