import xml.etree.ElementTree as ET
from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import DC, XSD, OWL, SKOS
import os

def xml_to_rdf(xml_file_path):
    # Define namespaces
    ASKG_DATA = Namespace("https://w3id.org/UniverseTBD/data/scholarly/")
    ASKG_ONTO = Namespace("https://w3id.org/UniverseTBD/onto/scholarly#")

    g = Graph()

    # Bind namespaces
    g.bind("askg-data", ASKG_DATA)
    g.bind("askg-onto", ASKG_ONTO)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    g.bind("skos", SKOS)

    # Extracting paper ID and title from the file name
    paper_id = os.path.splitext(os.path.basename(xml_file_path))[0]
    paper_title = paper_id.replace("_", " ")  # Replace underscores with spaces

    # Process paper information
    paper_uri = ASKG_DATA[f"Paper-{paper_id}"]
    g.add((paper_uri, RDF.type, ASKG_ONTO.Paper))
    g.add((paper_uri, RDFS.label, Literal("Paper label", lang="en")))
    g.add((paper_uri, DC.title, Literal(paper_title, datatype=XSD.string)))

    # Parse XML
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    for section in root.findall('.//section'):
        section_id = section.get('ID')
        section_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}"]
        g.add((section_uri, RDF.type, ASKG_ONTO.Section))
        g.add((paper_uri, ASKG_ONTO.hasSection, section_uri))
        section_title = section.find('title').text if section.find('title') is not None else "No title"
        g.add((section_uri, RDFS.label, Literal(section_title, lang="en")))

        # Add paragraphs and sentences logic as per your XML structure
        # ...

    return g

def main():
    # Input XML file
    input_xml_path = "deep_document_model_final_version.xml"

    # Process the XML file
    rdf_graph = xml_to_rdf(input_xml_path)

    # Output RDF file
    output_rdf_path = "output.rdf"
    rdf_graph.serialize(destination=output_rdf_path, format='xml')

    print(f"RDF data has been saved to {output_rdf_path}!")

if __name__ == "__main__":
    main()
