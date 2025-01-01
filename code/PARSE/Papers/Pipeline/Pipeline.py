"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/3/2023 11:52 pm
"""
import os

import pdf2md
import parse_md

def main():
    input_dir = "./papers"  # Directory containing PDF files
    output_dir = "./markdown"  # Directory for output Markdown files

    # pdf2md.convert_pdfs_to_markdown(input_dir, output_dir)

    # Create output directory if it doesn't exist
    os.makedirs("./output", exist_ok=True)

    for md_file in os.listdir(output_dir):
        if md_file.lower().endswith('.md'):
            md_path = os.path.join(output_dir, md_file)
            file_name = os.path.splitext(md_file)[0]
            output_ttl = f"./output/{file_name}.ttl"

            # Check if TTL file already exists
            if os.path.exists(output_ttl):
                print(f"Skipping {md_file} - TTL file already exists")
                continue

            print(f"Processing {md_file}...")
            parse_md.process_markdown_file(
                input_file=md_path,
                output_ttl=output_ttl,
                paper_id=file_name
            )


if __name__ == "__main__":
    main()