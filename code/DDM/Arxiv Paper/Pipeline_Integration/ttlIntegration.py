from rdflib import Graph

# Load TTL file
ttl_file_path = 'C:/Users/6/Desktop/Arxiv/Experiment/IntegratedTTL/ASKG_Integrated_10.ttl'  # 替换为你的TTL文件路径

g = Graph()
g.parse(ttl_file_path, format="ttl")


# Query the labels of all Academic Entities
query_academic_entities = """
PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?entity ?label WHERE {
  ?entity a askg-onto:AcademicEntity ;
          rdfs:label ?label .
}
"""

#Query the text and corresponding identifiers of all Excerpts' inSentences
query_excerpts = """
PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?excerpt WHERE {
  ?excerpt a askg-data:Excerpt .
}
"""

# query_excerpts = """
# PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
# PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#
# SELECT ?excerpt ?inSentence WHERE {
#   ?excerpt a askg-data:Excerpt ;
#            askg-onto:inSentence ?inSentence .
# }
# """
# Query the text and corresponding identifiers of all Paragraphs
query_paragraphs = """
PREFIX askg-onto: <https://www.anu.edu.au/onto/scholarly#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?paragraph ?label WHERE {
  ?paragraph a askg-onto:Paragraph ;
             rdfs:label ?label .
}
"""

# Do the Query
excerpts = {inSentence.value: excerpt for excerpt, inSentence in g.query(query_excerpts)}
paragraphs = {label.value: paragraph for paragraph, label in g.query(query_paragraphs)}
# Execute the query
results = g.query(query_academic_entities)

print(f"Found {len(excerpts)} excerpts and {len(paragraphs)} paragraphs.")
print(f"Total triples in the graph: {len(g)}")

# 寻找完全匹配的Excerpt和Paragraph
for excerpt_text, excerpt_uri in excerpts.items():
    if excerpt_text in paragraphs:
        paragraph_uri = paragraphs[excerpt_text]
        print(f"Exact match found: {excerpt_uri} is part of {paragraph_uri}")
    else:
        print(f"No exact match found for excerpt: {excerpt_uri}")





