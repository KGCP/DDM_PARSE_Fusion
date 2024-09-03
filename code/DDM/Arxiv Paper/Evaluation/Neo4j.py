
from neo4j import GraphDatabase
from py2neo import Graph

if __name__ == '__main__':

    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = '12345678'

    neo4j_graph = Graph(uri, auth = (username, password))

    neo4j_graph.run("MATCH (n) DETACH DELETE n")

    try:
        #initalize graph, add constraint to graph
        neo4j_graph.run("CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource) \
            REQUIRE r.uri IS UNIQUE")
    except:
        pass

    # neo4j_graph.run("CALL n10s.graphconfig.init()")

    neo4j_graph.run("CALL n10s.graphconfig.init({ handleVocabUris: 'MAP'})")

    KG_path = "C:/Users/6/Desktop/Arxiv/Experiment/ASKG_Demo.ttl"
    result = neo4j_graph.run(f"CALL n10s.rdf.import.fetch('{KG_path}', 'Turtle')")

    for record in result:
        print(record)




