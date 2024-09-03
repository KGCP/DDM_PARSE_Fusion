from rdflib import Graph
import json

def convert_ttl_to_json(ttl_file_path, json_file_path):
    # 创建RDF图并解析TTL文件
    g = Graph()
    g.parse(ttl_file_path, format='n3')  # 使用'n3'格式解析，它通常与Turtle兼容

    # 提取RDF图中的所有三元组
    triples = []
    for subj, pred, obj in g:
        triples.append({
            "subject": str(subj),
            "predicate": str(pred),
            "object": str(obj)
        })

    # 将三元组转换为JSON字符串
    json_data = json.dumps(triples, indent=2)

    # 将JSON数据写入文件
    with open(json_file_path, 'w') as json_file:
        json_file.write(json_data)

    print(f"Conversion completed. JSON file saved to: {json_file_path}")

# 使用示例
ttl_file = 'C:/Users/6/Desktop/Arxiv/Experiment/DDM_ttl/A_Pipeline_for_Analysing_Grant_Applications.ttl'  # 替换为您的TTL文件路径
json_file = 'C:/Users/6/Desktop/Arxiv/Experiment/DDM_ttl/A_Pipeline_for_Analysing_Grant_Applications.json'    # 您希望保存的JSON文件路径

convert_ttl_to_json(ttl_file, json_file)
