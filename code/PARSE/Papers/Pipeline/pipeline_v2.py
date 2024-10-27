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


def parse_markdown(md_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)
    return html_content


def parse_json(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        structure = json.load(f)
    return structure['toc']


def clean_text(text):
    # Remove HTML tags and unescape HTML entities
    clean = re.sub(r'<[^>]+>', '', text)
    clean = html.unescape(clean)
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def build_document_structure(html_content, toc):
    doc = ET.Element("section")
    current_section = doc
    for index, item in enumerate(toc, start=1):
        section = ET.SubElement(current_section, "section")
        section.set("ID", str(item['page_index'] + 1))
        section.set("index", str(index))
        heading = ET.SubElement(section, "heading")
        heading.text = item['title']
        content = html_content.split(item['title'])[1].split(item['title'])[0] if len(
            html_content.split(item['title'])) > 1 else ""
        paragraphs = content.split('\n\n')
        for p_index, p in enumerate(paragraphs, start=1):
            if p.strip():
                para = ET.SubElement(section, "paragraph")
                para.set("ID", f"{item['page_index'] + 1}.{p_index}")
                para.set("index", str(p_index))
                para_text = ET.SubElement(para, "text")
                para_text.text = clean_text(p)
                sentences = re.split(r'(?<=[.!?]) +', clean_text(p))
                for s_index, s in enumerate(sentences, start=1):
                    if s.strip():
                        sent = ET.SubElement(para, "sentence")
                        sent.set("ID", f"{item['page_index'] + 1}.{p_index}.{s_index}")
                        sent.set("index", str(s_index))
                        sent_text = ET.SubElement(sent, "text")
                        sent_text.text = s.strip()
        current_section = section
    return doc


def generate_xml(doc, output_file):
    tree = ET.ElementTree(doc)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)


def generate_ttl(doc, output_file, paper_id, paper_title):
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

    paper_uri = ASKG_DATA[f"Paper-{paper_id}"]
    g.add((paper_uri, RDF.type, ASKG_ONTO.Paper))
    g.add((paper_uri, RDFS.label, Literal(paper_title, lang="en")))
    g.add((paper_uri, DC.title, Literal(paper_title, datatype=XSD.string)))

    for section in doc.findall(".//section"):
        section_id = section.get("ID")
        section_index = section.get("index")
        section_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}"]
        g.add((section_uri, RDF.type, ASKG_ONTO.Section))
        g.add((paper_uri, ASKG_ONTO.hasSection, section_uri))
        g.add((section_uri, RDFS.label, Literal(f"Section {section_index}", lang="en")))
        g.add((section_uri, index_predicate, Literal(section_index, datatype=XSD.int)))
        heading = section.find("heading")
        if heading is not None:
            g.add((section_uri, DOMO.Text, Literal(heading.text, lang="en")))

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

    g.serialize(destination=output_file, format='turtle')


def main(input_dir, output_dir):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Find input files
    md_file = os.path.join(input_dir, 'test.md')
    json_file = os.path.join(input_dir, 'A_Pipeline_for_Analysing_Grant_Applications_meta.json')

    # Parse input files
    html_content = parse_markdown(md_file)
    toc = parse_json(json_file)

    # Build document structure
    doc = build_document_structure(html_content, toc)

    # Generate output file names based on input file name
    base_name = os.path.splitext(os.path.basename(md_file))[0]
    paper_id = base_name
    paper_title = base_name.replace('_', ' ')

    # Generate TTL output
    ttl_output = os.path.join(output_dir, f"{base_name}_ddm.ttl")
    generate_ttl(doc, ttl_output, paper_id, paper_title)
    print(f"TTL file generated: {ttl_output}")


if __name__ == "__main__":
    input_dir = r"./papers"
    output_dir = r"./output"
    main(input_dir, output_dir)