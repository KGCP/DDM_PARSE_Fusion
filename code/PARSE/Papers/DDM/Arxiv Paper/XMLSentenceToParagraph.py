import os
from xml.etree.ElementTree import parse, tostring


def process_xml(xml_file_path):
    tree = parse(xml_file_path)
    root = tree.getroot()

    for paragraph in root.iter('paragraph'):
        for reference in list(paragraph.iter('reference')):
            ref_parent = reference.getparent()
            if ref_parent is not None:
                ref_parent.remove(reference)
            paragraph.append(reference)

    for paragraph in root.iter('paragraph'):
        paragraph_text = ""
        for sentence in list(paragraph.iter('sentence')):
            paragraph_text += sentence.text if sentence.text else ""
            paragraph.remove(sentence)
        if paragraph_text:
            if paragraph.text:
                paragraph.text += paragraph_text
            else:
                paragraph.text = paragraph_text

    modified_xml_content = tostring(root, encoding='unicode')
    return modified_xml_content


def process_xml_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            xml_file_path = os.path.join(folder_path, filename)
            print(f"Processing {xml_file_path}...")
            modified_xml_content = process_xml(xml_file_path)

            # Save the modified content back to the original file
            with open(xml_file_path, 'w', encoding='utf-8') as modified_file:
                modified_file.write(modified_xml_content)


# 设置包含XML文件的文件夹路径
folder_path = 'path_to_your_folder'  # 替换为您的文件夹路径
process_xml_files_in_folder(folder_path)
