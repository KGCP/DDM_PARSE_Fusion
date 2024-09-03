import hashlib
import xml.etree.ElementTree as ET
from rdflib import Graph, Literal, Namespace, RDF, RDFS, XSD, URIRef
from rdflib.namespace import DC, OWL, SKOS

def convert_xml_to_turtle(embedded_references_xml_content, turtle_file_path, paper_id, section_titles, paper_title):
    # Define namespaces
    ASKG_DATA = Namespace("https://w3id.org/UniverseTBD/data/scholarly/")
    ASKG_ONTO = Namespace("https://w3id.org/UniverseTBD/onto/scholarly#")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
    DC = Namespace("http://purl.org/dc/elements/1.1/")

    g = Graph()

    # Bind namespaces
    g.bind("askg-data", ASKG_DATA)
    g.bind("askg-onto", ASKG_ONTO)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    g.bind("skos", SKOS)
    g.bind("dc", DC)

    paper_uri = ASKG_DATA[f"Paper-{paper_id}"]
    g.add((paper_uri, RDF.type, ASKG_ONTO.Paper))
    g.add((paper_uri, RDFS.label, Literal("Paper label", lang="en")))
    g.add((paper_uri, DC.title, Literal(paper_title, datatype=XSD.string)))

    root = ET.fromstring(embedded_references_xml_content)
    for section in root.findall('.//section'):
        section_id = section.get('ID')
        section_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}"]
        g.add((section_uri, RDF.type, ASKG_ONTO.Section))
        g.add((paper_uri, ASKG_ONTO.hasSection, section_uri))
        section_title = section_titles.get(section_id, "Section label")
        g.add((section_uri, RDFS.label, Literal(section_title, lang="en")))

        for paragraph in section.findall('./paragraph'):
            paragraph_id = paragraph.get('ID')
            paragraph_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}-Paragraph-{paragraph_id}"]
            g.add((paragraph_uri, RDF.type, ASKG_ONTO.Paragraph))
            g.add((section_uri, ASKG_ONTO.hasParagraph, paragraph_uri))
            g.add((paragraph_uri, RDFS.label, Literal("Paragraph label", lang="en")))

            for sentence in paragraph.findall('./sentence'):
                sentence_id = sentence.get('ID')
                sentence_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}-Paragraph-{paragraph_id}-Sentence-{sentence_id}"]
                g.add((sentence_uri, RDF.type, ASKG_ONTO.Sentence))
                g.add((paragraph_uri, ASKG_ONTO.hasSentence, sentence_uri))
                g.add((sentence_uri, RDFS.label, Literal("Sentence label", lang="en")))

    turtle_content = g.serialize(format='turtle')
    with open(turtle_file_path, 'wb') as file:
        file.write(turtle_content.encode('utf-8'))

    print(f"Turtle file generated at: {turtle_file_path}")

# Example usage
xml_file_path = 'path_to_your_xml_file.xml'
turtle_file_path = 'output_file.ttl'
paper_title = "Your Paper Title"
paper_id = hashlib.md5(paper_title.encode()).hexdigest()

# Read XML content
with open(xml_file_path, 'r', encoding='utf-8') as file:
    xml_content = file.read()

# Convert XML to Turtle
convert_xml_to_turtle(xml_content, turtle_file_path, paper_id, {}, paper_title)
