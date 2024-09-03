"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 27/3/2023 9:38 pm
"""
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef, XSD, OWL, SKOS, DC, RDFS
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib.plugins.sparql import prepareQuery

ASKG_namespace = Namespace("https://www.anu.edu.au/onto/scholarly")
DOMO_namespace = Namespace("https://www.anu.edu.au/onto/domo")
WIKIDATA_namespace = Namespace("http://www.wikidata.org")
def load_ASKG(path):
    #load ASKG RDF graph
    ASKG = Graph()
    ASKG.parse(path, format="turtle")
    ASKG.bind("askg", ASKG_namespace)
    ASKG.bind("domo", DOMO_namespace)
    ASKG.bind("wd", WIKIDATA_namespace)
    ASKG.bind("skos", SKOS)
    ASKG.bind("dc", DC)
    return ASKG

def get_hot_topics(ASKG, limit=10):
    # Define the SPARQL query to get the most popular academic entities based on their mentions in papers
    sparql_query = """
    SELECT ?academic_entity (COUNT(DISTINCT ?paper) AS ?paper_count) WHERE {
      ?academic_entity a askg:AcademicEntity .
      ?academic_entity rdfs:label ?academic_entity_label .
      FILTER(REGEX(STR(?academic_entity_label), "keyword", "i"))
      ?academic_entity owl:sameAs ?wikidata_entity .
      ?paper askg:mentions ?academic_entity .
      ?paper domo:paper_id ?paper_id .
      ?paper domo:year ?year .
      FILTER(?year >= 2020)
        }
        GROUP BY ?academic_entity
        ORDER BY DESC(?paper_count)
        LIMIT 10 """

    # Prepare and execute the query
    query = prepareQuery(sparql_query, initNs={'askg': ASKG_namespace})
    results = ASKG.query(query)

    # Extract the results and return them as a list of tuples
    hot_topics = []
    for row in results:
        academic_entity = str(row[0])
        count = int(row[1])
        hot_topics.append((academic_entity, count))

    return hot_topics

if __name__ == "__main__":
    ASKG_path = "../backup/ASKG.ttl"
    ASKG = load_ASKG(ASKG_path)

    query = """
    SELECT ?keyword (COUNT(?paper) AS ?paper_count)
    WHERE {
      ?paper rdf:type askg:Paper .
      ?paper askg:hasSection ?section .
      ?section askg:contains ?excerpt .
      ?excerpt askg:mentions ?academic_entity .
      ?academic_entity skos:broader ?scientific_type .
      ?scientific_type rdfs:label ?research_field .
      ?academic_entity askg:entityName ?keyword .
      FILTER (LANG(?research_field) = "en")
    }
    GROUP BY ?keyword
    ORDER BY DESC(?paper_count)
    LIMIT 10
    """

    # Replace 'Research Field' with the desired research field
    research_field = "Research Field"
    result = ASKG.query(query, initBindings={'research_field': Literal(research_field)})
    for row in result:
        print(f"{row.keyword}: {row.paper_count}")

    hot_topics = get_hot_topics(ASKG, limit=10)
    print("热门话题：")
    for topic, count in hot_topics:
        print(f"{topic}: {count}")


query = """
SELECT ?entity1 ?entity2
WHERE {
  ?excerpt rdf:type askg:Excerpt .
  ?excerpt askg:mentions ?entity1 .
  ?excerpt askg:mentions ?entity2 .
  ?entity1 rdf:type askg:AcademicEntity .
  ?entity2 rdf:type askg:AcademicEntity .
  FILTER (?entity1 != ?entity2)
}
"""