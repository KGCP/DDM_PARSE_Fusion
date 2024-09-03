from rdflib import Graph

# Load your TTL file
ttl_file_path = 'C:/Users/6/Desktop/Arxiv/Experiment/IntegratedTTL/ASKG_Integrated_10.ttl'  # 修改为你的文件路径
g = Graph()
g.parse(ttl_file_path, format="ttl")

excerpts = []
paragraphs = []

# 遍历图中的所有三元组
for s, p, o in g:
    # 根据你的数据结构调整条件，假设inSentence的谓语具有唯一标识
    if 'inSentence' in p:
        excerpts.append((str(s), str(o)))
    # 同样，假设label的谓语用于标识Paragraph，且URI中包含"Paragraph"字符串
    elif 'label' in p and 'Paragraph' in str(s):
        paragraphs.append((str(s), str(o)))

# 初始化匹配计数器
matched_excerpts_count = 0

# Performs a simple substring match
for excerpt_uri, excerpt_text in excerpts:
    match_found = False  # Flag whether a match was found
    for paragraph_uri, paragraph_text in paragraphs:
        if excerpt_text in paragraph_text:
            matched_excerpts_count += 1
            match_found = True
            break  # Once a match is found, there is no need to continue searching in other paragraphs

# Print Output
print(f"Total excerpts: {len(excerpts)}")
print(f"Excerpts matched with a paragraph: {matched_excerpts_count}")
