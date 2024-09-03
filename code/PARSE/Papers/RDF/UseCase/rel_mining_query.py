import rdflib
from rdflib.plugins.sparql import prepareQuery


def get_authors_with_mentions_query():
    query = """
    PREFIX askg-data: <https://www.anu.edu.au/onto/scholarly/>
    PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
    PREFIX domo: <https://www.anu.edu.au/onto/domo#>

    SELECT ?author (COUNT(?excerpt) as ?mentionCount) WHERE {
      ?paper a askg-onto:Paper ;
             askg-onto:hasAuthor ?author ;
             askg-onto:hasSection ?section .
      ?section askg-onto:contains ?excerpt .
      ?excerpt askg-onto:mentions askg-data:AcademicEntity-computational_linguistics-Q182557 .
    } GROUP BY ?author
      HAVING (COUNT(?excerpt) >= 1)
    """
    return query


if __name__ == "__main__":
    graph = rdflib.Graph()
    graph.parse("ASKG_rel_mining.ttl", format="turtle")

    query = get_authors_with_mentions_query()

    prepared_query = prepareQuery(query)
    results = graph.query(prepared_query)

    for result in results:
        author, mention_count = result
        print(f"Author: {author}, Mention Count: {mention_count}")
