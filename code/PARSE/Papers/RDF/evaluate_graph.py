import rdflib
from rdflib.namespace import RDF
import networkx as nx

# 1. Load RDF graph
g = rdflib.Graph()
g.parse("ASKG_merged_step.ttl", format="ttl")

# 2. Convert RDF graph to NetworkX graph
nx_graph = nx.DiGraph()

for s, p, o in g:
    nx_graph.add_edge(s, o, predicate=p)

# 3. Calculate the number of relationship types
predicate_types = set(p for s, p, o in g)
print(f"Number of relationship types: {len(predicate_types)}")

# 4. Calculate the number of entity types
entity_types = set([o for s, p, o in g.triples((None, RDF.type, None))])
print(f"Number of entity types: {len(entity_types)}")

# 5. Calculate average degree
average_degree = sum(dict(nx_graph.degree()).values()) / nx_graph.number_of_nodes()
print(f"Average degree: {average_degree}")

# 6. Calculate clustering coefficient (converting directed graph to undirected graph)
undirected_nx_graph = nx_graph.to_undirected()
clustering_coefficient = nx.average_clustering(undirected_nx_graph)
print(f"Clustering coefficient: {clustering_coefficient}")

# 7. Calculate the number of connected components
connected_components = [c for c in nx.connected_components(undirected_nx_graph)]
print(f"Number of connected components: {len(connected_components)}")

# 9. Calculate information density
information_density = nx_graph.number_of_edges() / nx_graph.number_of_nodes()
print(f"Information density: {information_density}")

# 10. Count triples
triple_count = len(g)
print(f"Number of triples: {triple_count}")

# 11. Count entities
entities = set(s for s, _, _ in g) | set(o for _, _, o in g)
entity_count = len(entities)
print(f"Number of entities: {entity_count}")

