import os
import subprocess
import xml.etree.ElementTree as ET
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import re
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, DC

# Step 1: Convert PDF to HTML using Docker and pdf2htmlEX
def convert_pdf_to_html(pdf_path, html_path):
    pdf_dir = os.path.dirname(os.path.abspath(pdf_path))
    pdf_filename = os.path.basename(pdf_path)
    # 运行 Docker 命令，转换 PDF 到 HTML
    subprocess.run(['docker', 'run', '-ti', '--rm', '-v', f"{pdf_dir}:/pdf", 'bwits/pdf2htmlex', 'pdf2htmlEX', f"/pdf/{pdf_filename}"], check=True)
    # HTML文件的名称与PDF文件相同（除了扩展名）
    generated_html_path = os.path.join(pdf_dir, f"{os.path.splitext(pdf_filename)[0]}.html")
    # 如果指定的html_path与生成的HTML文件路径不同，则移动文件
    if generated_html_path != html_path:
        os.rename(generated_html_path, html_path)
    # 确保生成的 HTML 文件存在
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"Expected HTML file not found: {html_path}")



# Step 2: Extract headings from HTML to XML (Your implementation)
def extract_headings_to_xml(html_path, headings_xml_path):
    # Load the HTML file
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    headings = [a_tag.text for a_tag in soup.find_all("a", class_="l") if a_tag.text.strip() != ""]

    # Create the root element
    root = ET.Element("section")
    parents = {0: root}

    max_main_id = 0  # 用于跟踪最大的主标题ID

    # Process and add each heading to the XML structure
    for heading in headings:
        level = determine_level(heading)
        id_part = heading.split()[0]
        # 尝试提取主标题ID（即小数点前的部分）
        main_id = int(id_part.split('.')[0]) if '.' in id_part else int(id_part)
        max_main_id = max(max_main_id, main_id)  # 更新最大的主标题ID

        section_elem = ET.Element("section", ID=heading.split()[0])
        heading_elem = ET.SubElement(section_elem, "heading")
        heading_elem.text = " ".join(heading.split()[1:])
        if level not in parents:
            parents[level] = parents[level-1]
        parents[level].append(section_elem)
        parents[level + 1] = section_elem

    # Dynamically assign an ID to the Reference section
    reference_id = str(max_main_id + 1)
    reference_section_elem = ET.Element("section", ID=reference_id)
    reference_heading_elem = ET.SubElement(reference_section_elem, "heading")
    reference_heading_elem.text = "Reference"
    root.append(reference_section_elem)

    # Indent the XML for pretty printing
    indent(root)

    # Create the ElementTree object and save to XML file
    tree = ET.ElementTree(root)
    tree.write(headings_xml_path, encoding='utf-8', xml_declaration=True)


# Function to prettify the XML
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# Function to determine the level of the heading based on its format
def determine_level(heading):
    if " " not in heading:
        return 0
    first_word = heading.split()[0]
    if first_word.isdigit():
        return 1
    elif "." in first_word:
        return len(first_word.split("."))
    return 0


# Function to extract text from PDF
def extract_pdf_text(pdf_file):
    with fitz.open(pdf_file) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text

# Function to split text by headings
def split_text_by_headings(pdf_text, headings_xml):
    tree = ET.ElementTree(ET.fromstring(headings_xml))
    root = tree.getroot()
    headings = [elem.text for elem in root.iter('heading')]
    sections_text = {heading: "" for heading in headings}
    current_heading = None
    for line in pdf_text.split('\n'):
        if line.strip() in headings:
            current_heading = line.strip()
        elif current_heading:
            sections_text[current_heading] += line + "\n"
    return sections_text

# Function to improve readability
def improve_readability(sections_text):
    improved_sections = {}
    for heading, text in sections_text.items():
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        improved_sections[heading] = cleaned_text
    return improved_sections

def convert_xml_to_turtle(embedded_references_xml_content, turtle_file_path, paper_id):
    # 定义命名空间
    ASKG_DATA = Namespace("https://www.anu.edu.au/data/scholarly/")
    ASKG_ONTO = Namespace("https://www.anu.edu.au/onto/scholarly#")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

    g = Graph()

    # 绑定命名空间
    g.bind("askg-data", ASKG_DATA)
    g.bind("askg-onto", ASKG_ONTO)
    g.bind("owl", OWL)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    g.bind("skos", SKOS)

    paper_uri = ASKG_DATA[f"Paper-{paper_id}"]
    g.add((paper_uri, RDF.type, ASKG_ONTO.Paper))
    # 你需要从某处获取 label 和 title
    g.add((paper_uri, RDFS.label, Literal("Paper label", lang="en")))
    g.add((paper_uri, DC.title, Literal("Paper title", datatype=XSD.string)))

    root = ET.fromstring(embedded_references_xml_content)
    for section in root.findall('.//section'):
        section_id = section.get('ID')
        section_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}"]
        g.add((section_uri, RDF.type, ASKG_ONTO.Section))
        # 添加到论文
        g.add((paper_uri, ASKG_ONTO.hasSection, section_uri))
        # 你需要从某处获取每节的 label
        g.add((section_uri, RDFS.label, Literal("Section label", lang="en")))

        for paragraph in section.findall('./paragraph'):
            paragraph_id = paragraph.get('ID')
            paragraph_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}-Paragraph-{paragraph_id}"]
            g.add((paragraph_uri, RDF.type, ASKG_ONTO.Paragraph))
            # 添加到节
            g.add((section_uri, ASKG_ONTO.hasParagraph, paragraph_uri))
            # 你需要从某处获取每段的 label
            g.add((paragraph_uri, RDFS.label, Literal("Paragraph label", lang="en")))

            for sentence in paragraph.findall('./sentence'):
                sentence_id = sentence.get('ID')
                sentence_uri = ASKG_DATA[f"Paper-{paper_id}-Section-{section_id}-Paragraph-{paragraph_id}-Sentence-{sentence_id}"]
                g.add((sentence_uri, RDF.type, ASKG_ONTO.Sentence))
                # 添加到段落
                g.add((paragraph_uri, ASKG_ONTO.hasSentence, sentence_uri))
                # 你需要从某处获取每句的 label
                g.add((sentence_uri, RDFS.label, Literal("Sentence label", lang="en")))

    turtle_content = g.serialize(format='turtle')
    with open(turtle_file_path, 'wb') as file:
        file.write(turtle_content.encode('utf-8'))

    print(f"Turtle file generated at: {turtle_file_path}")



# Function to create DDM formatted XML
def create_ddm_formatted_xml(improved_sections, headings_xml):
    tree = ET.ElementTree(ET.fromstring(headings_xml))
    root = tree.getroot()
    for section in root.iter('section'):
        heading = section.find('heading')
        if heading is not None and heading.text in improved_sections:
            text = improved_sections[heading.text]
            sentences = re.split(r'(?<=[.!?]) +', text)
            for sentence in sentences:
                sentence_element = ET.SubElement(section, 'sentence')
                sentence_element.text = sentence
    return ET.tostring(root, encoding='unicode')

# Function to embed references in sentences
def embed_references_in_sentences(ddm_xml_content):
    tree = ET.ElementTree(ET.fromstring(ddm_xml_content))
    root = tree.getroot()
    reference_pattern = re.compile(r'\[(\d+)\]')
    for sentence in root.iter('sentence'):
        if sentence.text:
            references = reference_pattern.findall(sentence.text)
            for ref in references:
                sentence.text = sentence.text.replace(f'[{ref}]', '')
                reference_element = ET.SubElement(sentence, 'reference')
                reference_element.text = ref
    return ET.tostring(root, encoding='unicode')

# Main workflow
def main(pdf_path):
    base_name = os.path.splitext(pdf_path)[0]
    paper_id = os.path.basename(base_name)  # 提取文件名作为 paper_id
    html_path = f"{base_name}.html"
    headings_xml_path = f"{base_name}_headings.xml"
    ddm_xml_path = f"{base_name}_ddm.xml"
    turtle_file_path = f"{base_name}.ttl"
    convert_pdf_to_html(pdf_path, html_path)
    extract_headings_to_xml(html_path, headings_xml_path)

    headings_xml_content = open(headings_xml_path, 'r').read()
    pdf_text = extract_pdf_text(pdf_path)
    sections_text = split_text_by_headings(pdf_text, headings_xml_content)
    improved_sections_text = improve_readability(sections_text)
    ddm_formatted_xml_content = create_ddm_formatted_xml(improved_sections_text, headings_xml_content)
    embedded_references_xml_content = embed_references_in_sentences(ddm_formatted_xml_content)
    convert_xml_to_turtle(embedded_references_xml_content, turtle_file_path, paper_id)
    with open(ddm_xml_path, 'w', encoding='utf-8') as file:
        file.write(embedded_references_xml_content)

    print(f"DDM XML file generated at: {ddm_xml_path}")

if __name__ == "__main__":
    pdf_file_name = "C:/Users/6/Desktop/Arxiv/Pipeline/ASKG_paper.pdf"  # Replace with your actual PDF file name
    main(pdf_file_name)
