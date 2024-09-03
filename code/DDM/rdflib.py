# import json
# from rdflib import Graph, Namespace, URIRef, Literal, BNode
# from rdflib.namespace import RDF, XSD
#
# # 你的 JSON 数据
# json_data = """
# {
#     "name": "Alice",
#     "age": 30,
#     "friends": [
#         {"name": "Bob", "age": 31},
#         {"name": "Charlie", "age": 35}
#     ]
# }
# """
#
# # 解析 JSON 数据
# data = json.loads(json_data)
#
# # 创建一个 RDF Graph
# g = Graph()
#
# # 创建一个 namespace，可以用你的网站的 URL
# n = Namespace("http://example.com/")
#
# # 添加 Alice 到 graph 中
# alice = URIRef(n['Alice'])
# g.add((alice, RDF.type, n['Person']))
# g.add((alice, n['name'], Literal(data['name'], datatype=XSD.string)))
# g.add((alice, n['age'], Literal(data['age'], datatype=XSD.integer)))
#
# # 添加 Alice 的朋友们
# for friend in data['friends']:
#     # 使用 BNode 来表示朋友，因为我们没有他们的 URI
#     friend_node = BNode()
#     g.add((friend_node, RDF.type, n['Person']))
#     g.add((friend_node, n['name'], Literal(friend['name'], datatype=XSD.string)))
#     g.add((friend_node, n['age'], Literal(friend['age'], datatype=XSD.integer)))
#     # 添加 Alice 和朋友之间的关系
#     g.add((alice, n['hasFriend'], friend_node))
#
# # 打印出 graph 的所有 triples
# for s, p, o in g:
#     print(s, p, o)
