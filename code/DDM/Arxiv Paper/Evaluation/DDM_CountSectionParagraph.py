import xml.etree.ElementTree as ET


def count_tags(xml_file):
    # 初始化计数器
    section_count = 0
    paragraph_count = 0

    # 打开文件并按行读取，逐个解析
    with open(xml_file, 'r') as file:
        content = file.read()

    # 尝试单独解析每个部分
    fragments = content.split('</root>')  # 假设你的根标签名为'root'
    for fragment in fragments:
        if fragment.strip():
            try:
                # 为了形成完整的XML结构，需要确保每个片段都有根标签
                fragment = fragment + '</root>'
                root = ET.fromstring(fragment)

                # 计算<section>和<paragraph>标签的数量
                section_count += len(root.findall('.//section'))
                paragraph_count += len(root.findall('.//paragraph'))
            except ET.ParseError as e:
                print(f"Parse error: {e}")

    return section_count, paragraph_count




def count_xml_tags(filename):
    # 初始化计数器
    section_count = 0
    paragraph_count = 0

    # 打开文件并逐行读取
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            # 统计<section>标签的出现次数
            section_count += line.count('<section')
            # 统计<paragraph>标签的出现次数
            paragraph_count += line.count('<paragraph')

    return section_count, paragraph_count


# 指定文件路径
xml_file_path = 'C:/Users/6/Desktop/Arxiv/Dataset/ASKG_Integration.ttl'  # 这里替换为你的XML文件路径
section_count, paragraph_count = count_xml_tags(xml_file_path)

print(f"Number of <section> tags: {section_count}")
print(f"Number of <paragraph> tags: {paragraph_count}")

# 调用函数并传入你的XML文件路径
xml_file_path = 'C:/Users/6/Desktop/Arxiv/Experiment/Final_XML/Integrated_XML.xml'  # 修改为你的文件路径
section_count, paragraph_count = count_tags(xml_file_path)
print(f"Number of <section> tags: {section_count}")
print(f"Number of <paragraph> tags: {paragraph_count}")


