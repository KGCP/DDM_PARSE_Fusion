import re
import pdfplumber
import xml.etree.ElementTree as ET
from nltk.tokenize import sent_tokenize

def remove_invalid_chars(text):
    """Removes non-ASCII characters and multiple spaces."""
    if text and text[0] in ",.;:!?":
        text = text[1:].strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def get_references_updated(sentence):
    """Extracts references from the sentence, merges consecutive numbers, and returns the sentence without brackets."""
    references = re.findall(r'\[\d+\]', sentence)
    merged_references = []

    i = 0
    while i < len(references):
        current_ref = references[i].strip("[]")
        while i + 1 < len(references) and int(references[i].strip("[]")) + 1 == int(references[i+1].strip("[]")):
            current_ref += references[i+1].strip("[]")
            i += 1
        merged_references.append(current_ref)
        i += 1

    parts = []
    start = 0
    for ref in merged_references:
        idx = sentence.find('[' + ref + ']', start)
        parts.append((sentence[start:idx].strip(), ref))
        start = idx + len(ref) + 2
    if start < len(sentence):
        parts.append((sentence[start:].strip(), None))

    # Ensure each tuple in the list has two elements
    parts = [(part_text, ref if ref else '') for part_text, ref in parts if part_text and part_text.strip()]
    return parts


def extract_text_from_pdf(file_path):
    """Extracts text from the provided PDF file."""
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages)
    return text

def assign_section_ids(titles):
    """Assign section IDs based on the hierarchy of titles."""
    ids = []
    current_main = 0
    current_sub = 0
    for title in titles:
        if title in ['Introduction', 'Methodology', 'Experimental Settings', 'Experimental Result', 'Conclusion', 'References']:
            current_main += 1
            current_sub = 0
            ids.append(str(current_main))
        else:
            current_sub += 1
            ids.append(f"{current_main}.{current_sub}")
    return ids

def add_paragraph(root, title, paragraph, section_id):
    """Adds the given paragraph content under the specified section."""
    # Create a new section with the given section_id
    section = ET.SubElement(root, "section", ID=section_id)
    heading_element = ET.SubElement(section, "heading")
    heading_element.text = title

    # Split the paragraph into sub-paragraphs based on double newlines
    sub_paragraphs = paragraph.split('\n\n')
    for sub_paragraph in sub_paragraphs:
        if sub_paragraph:
            paragraph_element = ET.SubElement(section, "paragraph")
            sentences = sent_tokenize(sub_paragraph)
            for sentence_text in sentences:
                parts = get_references_updated(sentence_text)
                for part_text, refs in parts:
                    sentence_element = ET.SubElement(paragraph_element, "sentence")
                    sentence_element.text = remove_invalid_chars(part_text)
                    if refs:
                        for ref in refs:
                            reference_element = ET.SubElement(sentence_element, "reference")
                            reference_element.text = remove_invalid_chars(ref)

def find_section_by_title(root, title):
    """Finds the section with the given title in the XML structure."""
    for section in root.findall(".//section"):
        heading = section.find('heading')
        if heading is not None and heading.text == title:
            return section
    return None

def extract_reference_components(ref_text):
    """Extracts components of a reference."""
    ref_dict = {}
    ref_number_match = re.match(r'\[\d+\]', ref_text)
    if ref_number_match:
        ref_dict["ref_number"] = ref_number_match.group().strip("[]")
        ref_text = ref_text[ref_number_match.end():].strip()
        ref_parts = ref_text.split(",")
        if len(ref_parts) > 1:
            ref_dict["authors"] = ref_parts[0]
            ref_dict["title"] = ref_parts[1]
            if "arXiv" in ref_parts[-1]:
                ref_dict["journal"] = "arXiv preprint"
                ref_dict["year"] = re.search(r'\d{4}', ref_parts[-1]).group() if re.search(r'\d{4}', ref_parts[-1]) else None
            else:
                year_match = re.search(r'\d{4}', ref_parts[-1])
                if year_match:
                    ref_dict["year"] = year_match.group()
                    ref_dict["journal"] = ref_parts[-1][:year_match.start()].strip()
    return ref_dict

# Main code to extract content and create the Deep Document Model

# Extract the text from the PDF
pdf_file_path = "ASKG_paper.pdf"  # Adjust this path if needed
text = extract_text_from_pdf(pdf_file_path)

# Split the extracted text based on the known section titles
titles_text = [
    'Introduction',
    'Related Work',
    'Computer science in evaluating grant applications',
    'Term vectors and statistical measures in text representation',
    'Data mining models in text classification',
    'Methodology',
    'Data set',
    'Text pre-processing for grant applications',
    'Selection of high, low and moderate IC-score research proposals',
    'Design and apply the feature extraction technique',
    'Apply data mining models with grant applications',
    'Analyse moderate IC-score grant applications',
    'Experimental Settings',
    'Experimental Result',
    'Conclusion',
    'References'
]

# Update the titles_text list to only include titles that appear in the text
titles_text = [title for title in titles_text if title in text]

# Create the initial XML structure based on the extracted headings
root = ET.Element("document")
for title in titles_text[:-1]:  # Exclude "References" as it will be handled separately
    section = ET.SubElement(root, "section")
    heading_element = ET.SubElement(section, "heading")
    heading_element.text = title

split_texts = re.split('|'.join(map(re.escape, titles_text)), text)[1:]

# Populate the XML structure with the extracted content
section_ids = assign_section_ids(titles_text)
for idx, title in enumerate(titles_text[:-1]):  # Exclude "References" as it will be handled separately
    add_paragraph(root, title, split_texts[idx], section_ids[idx])

# Process the References section
references_text = split_texts[-1]
references = references_text.split("[")[1:]
references_data = [extract_reference_components("[" + ref) for ref in references]

references_section = ET.SubElement(root, "section")
heading_element = ET.SubElement(references_section, "heading")
heading_element.text = "References"

for ref_data in references_data:
    if "ref_number" in ref_data:
        reference_element = ET.SubElement(references_section, "reference", ID=ref_data["ref_number"])
        if "authors" in ref_data:
            authors_element = ET.SubElement(reference_element, "authors")
            for author in ref_data["authors"].split("and"):
                author_element = ET.SubElement(authors_element, "author")
                author_element.text = author.strip()
        title_element = ET.SubElement(reference_element, "title")
        title_element.text = ref_data["title"].strip() if "title" in ref_data else ""
        journal_element = ET.SubElement(reference_element, "journal")
        journal_element.text = ref_data.get("journal", "").strip()
        year_element = ET.SubElement(reference_element, "year")
        year_element.text = ref_data.get("year", "").strip()

# Save the final XML structure
xml_output_path_ddm = "deep_document_model_final_version.xml"
tree = ET.ElementTree(root)
tree.write(xml_output_path_ddm, encoding="utf-8", xml_declaration=True)