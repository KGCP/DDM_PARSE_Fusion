import rdflib
import networkx as nx

# Load RDF graph from a TTL file
rdf_graph = rdflib.Graph()
rdf_graph.parse("your_ttl_file.ttl", format="turtle")

# Convert RDF graph to NetworkX graph
def rdf_to_networkx(rdf_graph):
    G = nx.DiGraph()
    for s, p, o in rdf_graph:
        G.add_edge(s, o, predicate=p)
    return G

G = rdf_to_networkx(rdf_graph)

# Calculate the number of entities between any two entities
def entity_distance(graph, source, target):
    try:
        shortest_path_length = nx.shortest_path_length(graph, source, target)
        # Number of entities in between = shortest path length - 1
        return shortest_path_length - 1
    except nx.NetworkXNoPath:
        return None

source = rdflib.URIRef("https://www.anu.edu.au/onto/scholarly/A")  # Replace with your entity URI
target = rdflib.URIRef("https://www.anu.edu.au/onto/scholarly/E")  # Replace with your entity URI

distance = entity_distance(G, source, target)
print(f"Number of entities between entity {source} and entity {target}: {distance}")












