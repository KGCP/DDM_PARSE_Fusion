"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 20/4/2023 12:46 am
"""

import rdflib

input_file = "2022_S1_RDF_Graph_Restored.ttl"
output_file = "Fixed_2022_S1_RDF_Graph_Restored.ttl"

# Load the RDF data from the input file
g = rdflib.Graph()
g.parse(input_file, format="turtle")

# Define old and new namespaces
namespaces = [
    {
        "old": rdflib.Namespace("https://www.anu.edu.au/onto/scholarly/kg#"),
        "new": rdflib.Namespace("https://www.anu.edu.au/onto/scholarly/"),
        "prefix": "askg-data"
    },
    {
        "old": rdflib.Namespace("http://linked.data.gov.au/def/agrif#"),
        "new": rdflib.Namespace("http://example.org/agrif/"),
        "prefix": "agrif"
    },
    {
        "old": rdflib.Namespace("http://linked.data.gov.au/def/agrif-metadata#"),
        "new": rdflib.Namespace("http://example.org/agrif-metadata/"),
        "prefix": "agrif-md"
    },
    {
        "old": rdflib.Namespace("http://purl.org/dc/terms/"),
        "new": rdflib.Namespace("http://example.org/dc/terms/"),
        "prefix": "dcterms"
    }
]

# Change the namespaces and update the triples
for namespace in namespaces:
    old_ns = namespace["old"]
    new_ns = namespace["new"]
    prefix = namespace["prefix"]

    g.namespace_manager.bind(prefix, new_ns)

    for s, p, o in g.triples((None, None, None)):
        if isinstance(s, rdflib.term.URIRef) and s.startswith(old_ns):
            g.remove((s, p, o))
            g.add((rdflib.URIRef(s.replace(old_ns, new_ns)), p, o))

# Serialize the updated graph as Turtle
with open(output_file, "w", encoding="utf-8") as f:
    serialized_data = g.serialize(format="turtle")
    if isinstance(serialized_data, bytes):
        serialized_data = serialized_data.decode("utf-8")
    f.write(serialized_data)

