from rdflib import Graph, URIRef, Literal, Namespace, RDFS

# 载入TTL文件
ttl_file_path = 'C:/Users/6/Desktop/Arxiv/Experiment/IntegratedTTL/ASKG_Integrated_10_updated.ttl'
g = Graph()
g.parse(ttl_file_path, format="ttl")

# 定义命名空间
ASKG_ONTO = Namespace("https://www.anu.edu.au/onto/scholarly#")

# 假设这些是从用户查询中找到的相关 AcademicEntity 的标签
query_keywords = ["knowledge graph completion", "accuracy", "completeness"]

# 找到与用户查询相关的 AcademicEntity
related_entities = []
for s, p, o in g.triples((None, RDFS.label, None)):
    if any(keyword.lower() in o.lower() for keyword in query_keywords):
        related_entities.append(s)

print(f"Found {len(related_entities)} academic entities related to the query.")


# Debug: Print how many excerpts each entity has
for entity in related_entities:
    excerpts = list(g.objects(entity, ASKG_ONTO.mentions))
    print(f"Entity: {entity} has {len(excerpts)} excerpts")

    for excerpt in excerpts:
        paragraphs = list(g.subjects(ASKG_ONTO.hasExcerpt, excerpt))
        print(f"Excerpt: {excerpt} is part of {len(paragraphs)} paragraphs")  # Debug info

        for paragraph in paragraphs:
            paragraph_text = g.value(paragraph, ASKG_ONTO['rdfs:label'])
            if paragraph_text:
                print(f"Paragraph Text: {paragraph_text}\n")
            else:
                print("No paragraph text found.")  # Debug info

