import difflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef, XSD, OWL, SKOS, DC, RDFS

ASKG = Graph()
old_ASKG = Graph()
ASKG_namespace_onto = Namespace("https://www.anu.edu.au/onto/scholarly#")
ASKG_namespace_data = Namespace("https://www.anu.edu.au/onto/scholarly/")
DOMO_namespace = Namespace("https://www.anu.edu.au/onto/domo#")
WIKIDATA_namespace = Namespace("http://www.wikidata.org/entity/")
TNNT_namespace = Namespace("https://soco.cecc.anu.edu.au/tool/TNNT#")
agrif_md_namespace = Namespace("http://linked.data.gov.au/def/agrif-metadata#")
ASKG.bind("askg-onto", ASKG_namespace_onto)
ASKG.bind("askg-data", ASKG_namespace_data)
ASKG.bind("domo", DOMO_namespace)
ASKG.bind("wd", WIKIDATA_namespace)
ASKG.bind("skos", SKOS)
ASKG.bind("dc", DC)
ASKG.bind("tnnt", TNNT_namespace)
old_ASKG.bind("askg-onto", ASKG_namespace_onto)
old_ASKG.bind("askg-data", ASKG_namespace_data)
old_ASKG.bind("domo", DOMO_namespace)
old_ASKG.bind("wd", WIKIDATA_namespace)
old_ASKG.bind("skos", SKOS)
old_ASKG.bind("dc", DC)
old_ASKG.bind("tnnt", TNNT_namespace)
old_ASKG.bind("agrif-md", agrif_md_namespace)


# Set a similarity threshold
similarity_threshold = 0.8

def similarity(str1, str2):
    seq = difflib.SequenceMatcher(None, str1, str2)
    return seq.ratio()

def merge():
    ASKG.parse("merged_ASKG.ttl", format="turtle")

    for s, p, o in ASKG:
        old_ASKG.add((s, p, o))

    # Iterate through papers in graph2
    for paper2 in ASKG.subjects(RDF.type, ASKG_namespace_onto.Paper):
        paper2_title = ASKG.value(subject=paper2, predicate=DC.title)

        # Iterate through papers in graph1
        for paper1 in old_ASKG.subjects(RDF.type, ASKG_namespace_onto.Paper):
            paper1_label = old_ASKG.value(subject=paper1, predicate=RDFS.label)

            if similarity(paper1_label, paper2_title) >= 0.8:  # Adjust the threshold as needed
                # Replace paper1 with paper2 in all triples where paper1 is an object
                for s, p, o in old_ASKG.triples((None, None, paper1)):
                    old_ASKG.remove((s, p, o))
                    old_ASKG.add((s, p, paper2))

                # Merge the properties of both Paper entities
                for p, o in old_ASKG.predicate_objects(subject=paper1):
                    ASKG.add((paper2, p, o))

                # Remove the Paper entity from graph1
                old_ASKG.remove((paper1, None, None))

                # No need to search for more papers in graph1
                break

    # Save the merged graph
    ASKG.serialize("merged_graph.ttl", format="turtle")


if __name__ == '__main__':
    merge()