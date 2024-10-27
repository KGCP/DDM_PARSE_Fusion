import markdown
import json
import xml.etree.ElementTree as ET
import re
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, DC, XSD, OWL, SKOS
import os
import html

# Define namespaces
ASKG_DATA = Namespace("https://www.anu.edu.au/data/scholarly/")
ASKG_ONTO = Namespace("https://www.anu.edu.au/onto/scholarly#")
DOMO = Namespace("http://example.org/domo/")

def parse_markdown_structure(md_content):
    """
    Parse markdown content and extract sections based on heading levels
    """
    # Split content into lines
    lines = md_content.split('\n')
    sections = []
    current_section = None
    current_text = []

    for line in lines:
        # Check if line is a header
        header_match = re.match(r'^(#{1,6})\s(.+)$', line)
        if header_match:
            # If we have a previous section, save its content
            if current_section is not None:
                current_section['content'] = '\n'.join(current_text).strip()
                sections.append(current_section)

            # Start new section
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            current_section = {
                'level': level,
                'title': title,
                'index': len(sections) + 1
            }
            current_text = []
        elif current_section is not None:
            current_text.append(line)

    # Don't forget to add the last section
    if current_section is not None:
        current_section['content'] = '\n'.join(current_text).strip()
        sections.append(current_section)

    return sections

def clean_text(text):
    """Clean text by removing HTML tags and extra whitespace"""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = html.unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def split_into_paragraphs(content):
    """Split content into paragraphs"""
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', content) if p.strip()]
    return paragraphs

def split_into_sentences(text):
    """Split paragraph into sentences"""
    sentences = re.split(r'(?<=[.!?])\s+', clean_text(text))
    return [s.strip() for s in sentences if s.strip()]

def build_document_structure(md_content):
    """Build XML document structure from markdown content"""
    sections = parse_markdown_structure(md_content)

    doc = ET.Element("section")
    current_section = doc

    for section in sections:
        section_elem = ET.SubElement(current_section, "section")
        section_elem.set("ID", str(section['index']))
        section_elem.set("index", str(section['index']))
        section_elem.set("level", str(section['level']))

        # Add heading
        heading = ET.SubElement(section_elem, "heading")
        heading.text = section['title']

        # Process paragraphs
        paragraphs = split_into_paragraphs(section['content'])
        for p_index, p in enumerate(paragraphs, start=1):
            if p.strip():
                para = ET.SubElement(section_elem, "paragraph")
                para.set("ID", f"{section['index']}.{p_index}")
                para.set("index", str(p_index))

                para_text = ET.SubElement(para, "text")
                para_text.text = clean_text(p)

                # Process sentences
                sentences = split_into_sentences(p)
                for s_index, s in enumerate(sentences, start=1):
                    if s.strip():
                        sent = ET.SubElement(para, "sentence")
                        sent.set("ID", f"{section['index']}.{p_index}.{s_index}")
                        sent.set("index", str(s_index))
                        sent_text = ET.SubElement(sent, "text")
                        sent_text.text = s.strip()

    return doc

def generate_ttl(doc, output_file, paper_id, paper_title):
    """Generate TTL file from XML document structure"""
    g = Graph()

    # Bind namespaces
    g.bind("askg-data", ASKG_DATA)
    g.bind("askg-onto", ASKG_ONTO)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    g.bind("skos", SKOS)
    g.bind("dc", DC)
    g.bind("domo", DOMO)

    # Create URIRef for index predicate
    index_predicate = URIRef(ASKG_ONTO + "index")
    level_predicate = URIRef(ASKG_ONTO + "level")

    # Create paper node
    paper_uri = ASKG_DATA[f"Paper-{paper_id}"]
    g.add((paper_uri, RDF.type, ASKG_ONTO.Paper))
    g.add((paper_uri, RDFS.label, Literal(paper_title, lang="en")))
    g.add((paper_uri, DC.title, Literal(paper_title, datatype=XSD.string)))

    # Process sections
    for section in doc.findall(".//section"):
        section_id = section.get("ID")
        section_index = section.get("index")
        section_level = section.get("level", "0")
        section_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}"]

        g.add((section_uri, RDF.type, ASKG_ONTO.Section))
        g.add((paper_uri, ASKG_ONTO.hasSection, section_uri))
        g.add((section_uri, RDFS.label, Literal(f"Section {section_index}", lang="en")))
        g.add((section_uri, index_predicate, Literal(section_index, datatype=XSD.int)))
        g.add((section_uri, level_predicate, Literal(section_level, datatype=XSD.int)))

        heading = section.find("heading")
        if heading is not None:
            g.add((section_uri, DOMO.Text, Literal(heading.text, lang="en")))

        # Process paragraphs
        for para in section.findall("paragraph"):
            para_id = para.get("ID")
            para_index = para.get("index")
            para_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}-Paragraph-{para_id}"]

            g.add((para_uri, RDF.type, ASKG_ONTO.Paragraph))
            g.add((section_uri, ASKG_ONTO.hasParagraph, para_uri))
            g.add((para_uri, RDFS.label, Literal(f"Paragraph {para_index}", lang="en")))
            g.add((para_uri, index_predicate, Literal(para_index, datatype=XSD.int)))

            para_text = para.find("text")
            if para_text is not None:
                g.add((para_uri, DOMO.Text, Literal(para_text.text, lang="en")))

            # Process sentences
            for sent in para.findall("sentence"):
                sent_id = sent.get("ID")
                sent_index = sent.get("index")
                sent_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}-Paragraph-{para_id}-Sentence-{sent_id}"]

                g.add((sent_uri, RDF.type, ASKG_ONTO.Sentence))
                g.add((para_uri, ASKG_ONTO.hasSentence, sent_uri))
                g.add((sent_uri, RDFS.label, Literal(f"Sentence {sent_index}", lang="en")))
                g.add((sent_uri, index_predicate, Literal(sent_index, datatype=XSD.int)))

                sent_text = sent.find("text")
                if sent_text is not None:
                    g.add((sent_uri, DOMO.Text, Literal(sent_text.text, lang="en")))

    # Serialize to TTL file
    g.serialize(destination=output_file, format='turtle')

def process_markdown_file(input_file, output_ttl, paper_id=None):
    """Main function to process markdown file and generate TTL"""
    # Read markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Use filename as paper_id if not provided
    if paper_id is None:
        paper_id = os.path.splitext(os.path.basename(input_file))[0]

    # Build document structure
    doc = build_document_structure(md_content)

    # Generate TTL
    generate_ttl(doc, output_ttl, paper_id, paper_id)

if __name__ == "__main__":
    process_markdown_file(
        input_file="./markdown/test.md",
        output_ttl="./output/test.ttl",
        paper_id="12345"
    )