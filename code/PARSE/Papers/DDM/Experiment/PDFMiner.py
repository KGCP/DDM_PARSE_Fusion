from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer

for page_layout in extract_pages("RPLKG Robust Prompt Learning with Knowledge Graph.pdf"):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            for text_line in element:
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Print each element and its location
                        print(character.get_text(), character.bbox)

def find_sentence_in_pdf(pdf_path, sentence):
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                if sentence in element.get_text():
                    # Print this sentence and its location
                    print(sentence, element.bbox)

# Use the function above
find_sentence_in_pdf('RPLKG Robust Prompt Learning with Knowledge Graph.pdf',
                     'The pre-trained large-scale model has become a de facto for many diverse tasks.')