#Integrate all ASKG ttls into one whole ttl file.

import os


def merge_ttl_files(source_folder, output_file):
    prefix_lines = [
        "@prefix askg-data: <https://w3id.org/ASKG/data/scholarly/> .",
        "@prefix askg-onto: <https://w3id.org/ASKG/onto/scholarly#> .",
        "@prefix dc: <http://purl.org/dc/elements/1.1/> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> ."
    ]

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(source_folder):
            if filename.endswith(".ttl"):
                file_path = os.path.join(source_folder, filename)
                with open(file_path, 'r', encoding='utf-8') as infile:
                    skip_prefix = True
                    for line in infile:
                        if skip_prefix and any(line.startswith(prefix) for prefix in prefix_lines):
                            continue
                        skip_prefix = False
                        outfile.write(line)
                    outfile.write('\n\n')  # Add 1-2 lines of separation between files


source_folder = 'C:/Users/6/Desktop/Arxiv/Dataset/ttl'  # Replace with your source folder path
output_file = 'C:/Users/6/Desktop/Arxiv/Dataset/merged_output.ttl'  # Replace with your desired output file path

merge_ttl_files(source_folder, output_file)
