# from rdflib import Graph, Namespace, Literal
# import re
#
# # Load TTL file
# ttl_file_path = 'C:/Users/6/Desktop/Arxiv/Experiment/IntegratedTTL/ASKG_Integrated_10_updated.ttl'
# g = Graph()
# g.parse(ttl_file_path, format="ttl")
#
# # List of entities identified from the user query
# #entities = ["knowledge graph completion", "accuracy", "completeness"]
# #entities = ["Data mining", "techniques", "Complex datasets", "Computer science research"]
# #entities = ["machine learning", "capabilities", "BCI"]
# entities = ["ontology_base", "data processing", "IoT", "efficiency"]
# #entities = ["name entity recognition", "extraction", "trend"]
#
# # Prepare a SPARQL query to find all academic entities that match any of the identified entities and are Paragraphs
# query_template = """
# PREFIX askg: <https://www.anu.edu.au/onto/scholarly#>
# PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
#
# SELECT ?entity ?label WHERE {{
#   ?entity rdfs:label ?label .
#   FILTER (
#     {conditions}
#   )
#   FILTER CONTAINS(STR(?entity), "Paragraph")
# }}
# """
#
# # Prepare the filter conditions to include all identified entities
# conditions = " || ".join([f'CONTAINS(LCASE(?label), "{entity.lower()}")' for entity in entities])
# query = query_template.format(conditions=conditions)
#
# # Execute the query
# results = g.query(query)
#
# print(f"Found {len(results)} Paragraph academic entities related to the query.")
# for result in results:
#     print(f"Entity: {result[0]}, Label: {result[1]}")

from rdflib import Graph, Namespace, Literal
import re

# Load TTL file
ttl_file_path = 'C:/Users/6/Desktop/Arxiv/Experiment/IntegratedTTL/ASKG_Integrated_10_updated.ttl'
g = Graph()
g.parse(ttl_file_path, format="ttl")

# 定义一组关键词
#entities = ["knowledge graph completion", "accuracy", "completeness"]
#entities = ["Data mining", "techniques", "Complex datasets", "Computer science research"]
#entities = ["machine learning", "capabilities", "BCI"]
#entities = ["ontology_base", "data processing", "IoT", "efficiency"]
#entities = ["name entity recognition", "extraction", "trend"]
#entities = ["target endpoint", "named graph", "efficiency", "accuracy", "data integration", "distributed SPARQL endpoints"]
#entities = ["ontologies", "interoperability", "user interfaces", "accurately mapping", "interpreting", "diverse gesture vocabularies"]
#entities = ["API-driven ontology data integration platforms", "standardization", "reuse", "gesture vocabularies", "devices", "user interfaces"]
#entities = ["central hub", "Wikidata", "Linked Data ecosystem", "identity", "equivalence relationships", "entities", "authoritative sources"]
entities = ["novel components", "embedding-based learning systems", "Open Path Rule Learner", "capability", "complex rules", "large-scale knowledge graphs"]



# Prepare a SPARQL query to find all academic entities that match any of the identified entities and are Paragraphs
query_template = """
PREFIX askg: <https://www.anu.edu.au/onto/scholarly#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?entity ?label WHERE {{
  ?entity rdfs:label ?label .
  FILTER (
    {conditions}
  )
  FILTER CONTAINS(STR(?entity), "Paragraph")
}}
"""

# Prepare the filter conditions to include all identified entities
conditions = " || ".join([f'CONTAINS(LCASE(?label), "{entity.lower()}")' for entity in entities])
query = query_template.format(conditions=conditions)

# Execute the query
results = g.query(query)

# 将查询结果转换为包含(段落URI, 段落文本)的列表
paragraphs_with_uris = [(str(result[0]), str(result[1])) for result in results]

# 定义一个函数来计算段落中关键词的出现频率
def keyword_frequency(paragraph, keywords):
    frequency = 0
    for keyword in keywords:
        frequency += paragraph.lower().count(keyword.lower())
    return frequency

# 为每个段落计算关键词频率，同时保留URI
paragraph_scores = [(paragraph_uri, paragraph_text, keyword_frequency(paragraph_text, entities)) for paragraph_uri, paragraph_text in paragraphs_with_uris]

# 根据关键词出现频率对段落进行排序
sorted_paragraphs = sorted(paragraph_scores, key=lambda x: x[2], reverse=True)

# 定义一个函数来输出顶部N个相关段落
def print_top_paragraphs(sorted_paragraphs, top_n):
    print(f"Top {top_n} most relevant paragraphs with their URIs:")
    for i in range(min(top_n, len(sorted_paragraphs))):
        paragraph_uri, paragraph_text, _ = sorted_paragraphs[i]
        print(f"\nParagraph {i+1} URI: {paragraph_uri}")
        print(f"Paragraph {i+1} Text: {paragraph_text}")
        print("Keyword Frequency:", sorted_paragraphs[i][2])
        print("------------------------------------------------")

# 假设你想获取顶部5个最相关的段落
print_top_paragraphs(sorted_paragraphs, 10)
