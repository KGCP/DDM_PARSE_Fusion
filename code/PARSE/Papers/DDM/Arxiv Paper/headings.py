from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

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

# Load the HTML file
with open("ASKG_paper.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")
headings = [a_tag.text for a_tag in soup.find_all("a", class_="l") if a_tag.text.strip() != ""]

# Create the root element
root = ET.Element("section")
parents = {0: root}

# Process and add each heading to the XML structure
for heading in headings:
    level = determine_level(heading)
    section_elem = ET.Element("section", ID=heading.split()[0])
    heading_elem = ET.SubElement(section_elem, "heading")
    heading_elem.text = " ".join(heading.split()[1:])
    if level not in parents:
        parents[level] = parents[level-1]
    parents[level].append(section_elem)
    parents[level + 1] = section_elem

# Add a Reference section at the end
reference_section_elem = ET.Element("section", ID="7")
reference_heading_elem = ET.SubElement(reference_section_elem, "heading")
reference_heading_elem.text = "Reference"
root.append(reference_section_elem)

# Indent the XML for pretty printing
indent(root)

# Create the ElementTree object and save to XML file
tree = ET.ElementTree(root)
tree.write("headings1.xml", encoding="utf-8", xml_declaration=True)

