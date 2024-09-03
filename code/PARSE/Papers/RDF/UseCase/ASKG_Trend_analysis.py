import rdflib
from rdflib.plugins.sparql import prepareQuery


def get_research_problems_query():
    query = """
PREFIX askg-data: <https://www.anu.edu.au/onto/scholarly/>
PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?academicEntity (COUNT(?excerpt) AS ?count)
WHERE {
    ?excerpt askg-onto:mentions ?academicEntity .
    ?academicEntity skos:broader askg-onto:ResearchProblem .
}
GROUP BY ?academicEntity
ORDER BY DESC(?count)
LIMIT 50
       """
    return query


if __name__ == "__main__":
    graph = rdflib.Graph()
    graph.parse("ASKG_253_NER_clean.ttl", format="turtle")

    query = get_research_problems_query()

    prepared_query = prepareQuery(query)
    results = graph.query(prepared_query)

    for result in results:
        academic_entity, count = result
        print(f"Academic Entity: {academic_entity}, Count: {count}")
