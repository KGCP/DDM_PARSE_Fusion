"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 3/4/2023 1:38 am
"""
import re
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.cluster import KMeans
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery

def getKeyword():

    g = Graph()
    g.parse("UTBD.ttl", format="turtle")

    query = prepareQuery("""
        PREFIX askg: <https://www.anu.edu.au/onto/scholarly#>

        SELECT ?keyword (COUNT(?keywordInstance) AS ?frequency)
        WHERE {
        ?keyword a askg:Keyword .
        ?keywordInstance askg:correspondsTo ?keyword .
        }
        GROUP BY ?keyword
        ORDER BY DESC(?frequency)
        LIMIT 100
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
    keywords = getKeyword()

    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModel.from_pretrained("bert-base-uncased")

    embeddings = []

    for keyword in keywords:
        inputs = tokenizer(keyword, return_tensors="pt")
        outputs = model(**inputs)
        embeddings.append(outputs[0][:, 0, :].detach().numpy())

    embeddings = np.vstack(embeddings)

    num_clusters = 10
    kmeans = KMeans(n_clusters=num_clusters)
    clusters = kmeans.fit_predict(embeddings)

    for i in range(num_clusters):
        cluster_keywords = [keywords[j] for j in range(len(keywords)) if clusters[j] == i]
        wordcloud = WordCloud(font_path=None, width=800, height=400, background_color="white").generate(" ".join(cluster_keywords))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.show()