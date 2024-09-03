#这个文件用来对比LLM产生的三个问题和原问题之间的相似度，首先运行下面这两行代码
#pip install spacy
#python -m spacy download en_core_web_md

import spacy

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_md")  # This model includes word vectors

# Original question and the generated questions
original_question = "How can ontology-based models improve the efficiency of data processing in IoT environments?"

generated_questions = [

"How does the BCI-O’s Actuation Model leverage the concepts from W3C/OGC and IoT community standards to enhance semantic interoperability in BCI-IoT integrated applications?",
"What are the specific benefits of integrating the SSN/SOSA standards into the BCI-O's Sense Model for improving the semantic interoperability and integration of BCI systems within IoT environments?",
"In developing the BCI-O ontology, what were the key considerations and methodologies employed to ensure the quality and effectiveness of the ontology in context-aware applications?"

]

# Calculate similarity scores
original_doc = nlp(original_question)
similarity_scores = [original_doc.similarity(nlp(question)) for question in generated_questions]
print(similarity_scores)
