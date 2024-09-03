import rdflib
from rdflib.plugins.sparql import prepareQuery

def get_same_author_query():
    query = """
        PREFIX askg-data: <https://www.anu.edu.au/onto/scholarly/>
        PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?author (COUNT(?author) AS ?count) WHERE {
          ?paper a askg-onto:Paper ;
                 askg-onto:hasAuthor ?authorResource .
          ?authorResource rdfs:label ?author .
        }
        GROUP BY ?author
        HAVING (COUNT(?author) > 1)
        """
    return query


def get_title_query():
    query = """
        PREFIX askg-data: <https://www.anu.edu.au/onto/scholarly/>
        PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
    
        SELECT ?title WHERE {
          askg-data:Paper-0f3855c297f7d1 dc:title ?title .
        }
    """
    return query


def get_abstract_query():
    query = """
        PREFIX askg-data: <https://www.anu.edu.au/onto/scholarly/>
        PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
        
        SELECT ?summary WHERE {
          ?paper a askg-onto:Paper ;
                 askg-onto:hasSection ?abstract .
          ?abstract a askg-onto:Abstract ;
                    askg-onto:summary ?summary .
          FILTER (?paper = askg-data:Paper-0f3855c297f7d1)
}
    """
    return query


def get_conference_query():
    query = """
        PREFIX askg-data: <https://www.anu.edu.au/onto/scholarly/>
        PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?conference ?label WHERE {
          ?paper a askg-onto:Paper ;
                 askg-onto:presentedIn ?conference .
          ?conference rdfs:label ?label .
          FILTER (?paper = askg-data:Paper-0f3855c297f7d1)
        }

        """
    return query

import rdflib
from rdflib.plugins.sparql import prepareQuery

def get_keyword_query():
    query = """
        PREFIX askg-data: <https://www.anu.edu.au/onto/scholarly/>
        PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
        PREFIX domo: <https://www.anu.edu.au/onto/domo#>
        
        SELECT ?keywordSection ?keyword WHERE {
          ?paper a askg-onto:Paper ;
                 askg-onto:hasSection ?abstract .
          ?abstract a askg-onto:Abstract ;
                    domo:keyword ?keywordSection .
          ?keywordSection askg-onto:correspondsTo ?keyword .
          FILTER (?paper = askg-data:Paper-0f3855c297f7d1)
        }
    """
    return query


def get_paper_by_author():
    query = """
        PREFIX askg-data: <https://www.anu.edu.au/onto/scholarly/>
        PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
        
        SELECT ?paper ?title WHERE {
          ?paper a askg-onto:Paper ;
                 dc:title ?title ;
                 askg-onto:hasAuthor askg-data:J_Wang .
        }
    """
    return query


if __name__ == "__main__":
    # 读取Turtle文件
    graph = rdflib.Graph()
    graph.parse("ASKG_Example_AND.ttl", format="turtle")

    query = get_paper_by_author()

    # 准备并执行查询
    prepared_query = prepareQuery(query)
    results = graph.query(prepared_query)

    # 输出查询结果
    for result in results:
        keyword_section, keyword = result
        print(f"Keyword: {keyword}")
