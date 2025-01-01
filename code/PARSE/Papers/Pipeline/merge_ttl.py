import os
from pathlib import Path
import re
import string

def is_meaningful_entity(label):
    """
    Check if an entity label is meaningful
    Returns True if the entity is meaningful, False otherwise
    """
    # Remove all special characters and numbers
    cleaned = re.sub(r'[^a-zA-Z\s]', ' ', label)

    # Split into words and filter out empty strings
    words = [w.strip() for w in cleaned.split() if w.strip()]

    # Check if there are any words with length >= 3
    meaningful_words = [w for w in words if len(w) >= 3 and w.lower() not in ['the', 'and', 'for']]

    # Return True if there's at least one meaningful word
    return len(meaningful_words) > 0

def clean_ttl_content(content):
    """Clean and filter TTL content"""
    # Split content into triples (entities)
    entities = content.split('\n\n')
    cleaned_entities = []

    for entity in entities:
        if not entity.strip():
            continue

        # Check if this is an entity definition
        if 'rdfs:label' in entity:
            # Extract the label
            label_match = re.search(r'rdfs:label\s*"([^"]+)"', entity)
            if label_match:
                label = label_match.group(1)
                # Only keep meaningful entities
                if is_meaningful_entity(label):
                    cleaned_entities.append(entity)
        else:
            # Keep non-entity triples (like prefixes)
            cleaned_entities.append(entity)

    return '\n\n'.join(cleaned_entities)

def merge_ttl_files(input_dir, output_file):
    if not os.path.exists(input_dir):
        print(f"Directory {input_dir} does not exist!")
        return

    try:
        ttl_files = list(Path(input_dir).glob('*.ttl'))
        print(f"Found {len(ttl_files)} TTL files")

        with open(output_file, 'w', encoding='utf-8', errors='ignore') as outfile:
            # Write prefix section
            outfile.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n")
            outfile.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
            outfile.write("@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n")

            total_entities = 0
            cleaned_entities = 0

            for i, ttl_file in enumerate(ttl_files, 1):
                print(f"Processing file {i}/{len(ttl_files)}: {ttl_file.name}")

                try:
                    with open(ttl_file, 'r', encoding='utf-8', errors='ignore') as infile:
                        content = infile.read()

                    # Count original entities
                    original_count = len(re.findall(r'rdfs:label', content))
                    total_entities += original_count

                    # Clean content
                    cleaned_content = clean_ttl_content(content)

                    # Count remaining entities
                    remaining_count = len(re.findall(r'rdfs:label', cleaned_content))
                    cleaned_entities += remaining_count

                    # Skip prefix declarations in subsequent files
                    if i > 1:
                        cleaned_content = re.sub(r'@prefix.*?\.\n', '', cleaned_content)

                    outfile.write(f"\n# From file: {ttl_file.name}\n")
                    outfile.write(cleaned_content)
                    outfile.write("\n")

                    print(f"  - Removed {original_count - remaining_count} irrelevant entities")

                except Exception as e:
                    print(f"Error processing file {ttl_file.name}: {str(e)}")
                    continue

        print(f"\nMerge completed! Output file: {output_file}")
        print(f"Output file size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
        print(f"Total entities processed: {total_entities}")
        print(f"Entities after cleaning: {cleaned_entities}")
        print(f"Removed entities: {total_entities - cleaned_entities}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    input_directory = "./output"
    output_file = "./merged_output_cleaned.ttl"

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    merge_ttl_files(input_directory, output_file)

if __name__ == "__main__":
    main()