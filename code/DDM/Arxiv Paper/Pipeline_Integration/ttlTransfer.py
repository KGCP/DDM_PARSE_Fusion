import hashlib
import os
from lxml import etree as ET
from rdflib import Graph, Literal, Namespace, RDF
from rdflib.namespace import DC, OWL, SKOS, RDFS, XSD


def convert_xml_to_turtle(xml_file_path, turtle_file_path):
    try:
        # Define namespaces
        ASKG_DATA = Namespace("https://w3id.org/ASKG/data/scholarly/")
        ASKG_ONTO = Namespace("https://w3id.org/ASKG/onto/scholarly#")

        g = Graph()

        # Bind namespaces
        g.bind("askg-data", ASKG_DATA)
        g.bind("askg-onto", ASKG_ONTO)
        g.bind("owl", OWL)
        g.bind("xsd", XSD)
        g.bind("dc", DC)
        g.bind("skos", SKOS)
        g.bind("rdfs", RDFS)

        # Parse XML content
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        paper_id = hashlib.md5(xml_file_path.encode()).hexdigest()
        paper_uri = ASKG_DATA[f"Paper-{paper_id}"]
        g.add((paper_uri, RDF.type, ASKG_ONTO.Paper))

        # Assuming the paper title is available as an attribute or you fetch it differently
        title_element = root.find('.//title')
        paper_title = title_element.text if title_element is not None and title_element.text is not None else "Unknown Title"
        g.add((paper_uri, DC.title, Literal(paper_title, datatype=XSD.string)))

        for paragraph in root.iter('paragraph'):
            paragraph_text = ''.join(paragraph.itertext()).strip()
            if paragraph_text:
                paragraph_id = paragraph.get('ID')
                if paragraph_id is None:
                    paragraph_id = hashlib.md5(paragraph_text.encode()).hexdigest()
                paragraph_uri = ASKG_DATA[f"Paper-{paper_id}-Paragraph-{paragraph_id}"]
                g.add((paragraph_uri, RDF.type, ASKG_ONTO.Paragraph))
                g.add((paper_uri, ASKG_ONTO.hasParagraph, paragraph_uri))

                g.add((paragraph_uri, RDFS.label, Literal(paragraph_text, lang="en")))

                # Handle references if any
                for reference in paragraph.findall('reference'):
                    reference_text = reference.text.strip() if reference.text is not None else ""
                    if reference_text:
                        ref_id = reference.get('ID')
                        if ref_id is None:
                            ref_id = hashlib.md5(reference_text.encode()).hexdigest()
                        ref_uri = ASKG_DATA[f"Paper-{paper_id}-Paragraph-{paragraph_id}-Reference-{ref_id}"]
                        g.add((ref_uri, RDF.type, ASKG_ONTO.Reference))
                        g.add((paragraph_uri, ASKG_ONTO.hasReference, ref_uri))
                        g.add((ref_uri, DC.description, Literal(reference_text, datatype=XSD.string)))

        # Serialize to Turtle format and save
        turtle_content = g.serialize(format='turtle')
        with open(turtle_file_path, 'wb') as file:
            file.write(turtle_content.encode('utf-8'))

        print(f"Turtle file generated at: {turtle_file_path}")
        return True
    except Exception as e:
        print(f"Error converting file {xml_file_path}: {e}")
        return False


def process_xml_files_in_folder_to_ttl(folder_path, target_folder):
    success_count = 0
    failure_count = 0
    failed_files = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):
            xml_file_path = os.path.join(folder_path, filename)
            turtle_file_path = os.path.join(target_folder, os.path.splitext(filename)[0] + '.ttl')
            success = convert_xml_to_turtle(xml_file_path, turtle_file_path)
            if success:
                success_count += 1
            else:
                failure_count += 1
                failed_files.append(filename)

    print(f"Number of successfully converted files: {success_count}")
    print(f"Number of failed conversions: {failure_count}")
    if failed_files:
        print("Failed to convert the following files:")
        for file in failed_files:
            print(file)


# Set the folder paths
folder_path = 'C:/Users/6/Desktop/Arxiv/Dataset/data'  # Replace with your folder path containing XML files
target_folder = 'C:/Users/6/Desktop/Arxiv/Dataset/ttl'  # Replace with your target folder path for TTL files

# Create the target folder if it doesn't exist
if not os.path.exists(target_folder):
    os.makedirs(target_folder)

process_xml_files_in_folder_to_ttl(folder_path, target_folder)
