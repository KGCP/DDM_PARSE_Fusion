import rdflib
from rdflib.namespace import RDF
import networkx as nx

# 1. Load RDF graph
g = rdflib.Graph()
g.parse("C:/Users/6/Desktop/ASKG.ttl", format="ttl")

# 2. Convert RDF graph to NetworkX graph
nx_graph = nx.DiGraph()

for s, p, o in g:
    nx_graph.add_edge(s, o, predicate=p)

# 6. Calculate clustering coefficient (converting directed graph to undirected graph)
undirected_nx_graph = nx_graph.to_undirected()
clustering_coefficient = nx.average_clustering(undirected_nx_graph)
print(f"Clustering coefficient: {clustering_coefficient}")

