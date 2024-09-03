import os
import shutil

def count_files_and_copy_large_xml(directory, target_directory):
    pdf_count = 0
    xml_count = 0
    large_xml_count = 0
    headings_count = 0

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.pdf'):
                pdf_count += 1
            elif file.endswith('.xml') and 'ddm' in file.lower():
                xml_count += 1
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > 15:
                        large_xml_count += 1
                        shutil.copy(file_path, os.path.join(target_directory, file))
            if 'headings' in file.lower():
                headings_count += 1

    return pdf_count, xml_count, large_xml_count, headings_count

directory = 'C:/Users/6/Desktop/Arxiv/Dataset/Arxiv_2022S1_cs'  # Replace with the target directory path

target_directory = 'C:/Users/6/Desktop/Arxiv/Dataset/data'  # Replace with the target directory path for large XML files
pdf_count, xml_count, large_xml_count, headings_count = count_files_and_copy_large_xml(directory, target_directory)

print(f"Number of PDF files: {pdf_count}")
print(f"Number of XML files with 'ddm' in the name: {xml_count}")
print(f"Number of XML files with 'ddm' in the name and with correct content: {large_xml_count}")
print(f"Number of files with 'headings' in the name: {headings_count}")
print(f"Large XML files have been copied to: {target_directory}")
