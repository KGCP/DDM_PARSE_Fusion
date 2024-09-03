from PyPDF2 import PdfReader

def extract_text(pdf_path):
    # Open the PDF file
    reader = PdfReader(pdf_path)
    text = ""
    # Iterate over each page
    for page in reader.pages:
        # Extract text from each page
        text += page.extract_text()
    return text

# Use the above function
text = extract_text('RPLKG Robust Prompt Learning with Knowledge Graph.pdf')
print(text)



from PyPDF2 import PdfReader

def extract_text(pdf_path):
    # Open the PDF file
    reader = PdfReader(pdf_path)
    text = ""
    # Iterate over each page
    for page in reader.pages:
        # Extract text from each page
        text += page.extract_text()
    return text

# Use the above function
text = extract_text('RPLKG Robust Prompt Learning with Knowledge Graph.pdf')

# Search for a specific sentence
sentence = 'there have been many research works of the pre-trained large-scale model on the individual domain'
if sentence in text:
    print("Found the sentence in the document!")
else:
    print("The sentence was not found in the document.")



from PyPDF2 import PdfReader

def extract_text(pdf_path):
    # Open the PDF file
    reader = PdfReader(pdf_path)
    text = ""
    # Iterate over each page
    for page in reader.pages:
        # Extract text from each page
        text += page.extract_text()
    return text

# Use the above function
text = extract_text('RPLKG Robust Prompt Learning with Knowledge Graph.pdf')

# Search for a specific sentence
sentence = 'The pre-trained large-scale model has become a de facto for many diverse tasks.'
if sentence in text:
    print("Found the sentence in the document!")
else:
    print("The sentence was not found in the document.")
