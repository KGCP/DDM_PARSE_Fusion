from bs4 import BeautifulSoup

# Load the HTML file
with open("RPLKG Robust Prompt Learning with Knowledge Graph.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Find all <a> tags and extract the text
headings = [a_tag.text for a_tag in soup.find_all("a", class_="l")]
print(headings)

import xml.etree.ElementTree as ET


def add_child(parent, text):
    child = ET.Element("heading")
    child.text = text
    parent.append(child)
    return child


root = ET.Element("root")
stack = [root]

for heading in headings:
    level = heading.count('.')
    current_level = len(stack) - 1

    if level > current_level:
        child = add_child(stack[-1], heading)
        stack.append(child)
    elif level < current_level:
        stack = stack[:level + 1]
        child = add_child(stack[-1], heading)
        stack.append(child)
    else:
        # Check the length of the stack
        if len(stack) > 1:
            child = add_child(stack[-2], heading)
            stack[-1] = child
        else:
            # If the stack only contains the root, add the child to the root
            child = add_child(stack[-1], heading)
            stack[-1] = child

tree = ET.ElementTree(root)
tree.write("headings.xml", encoding="utf-8", xml_declaration=True)
