import os
import rdflib
from ctransformers import AutoModelForCausalLM, AutoTokenizer
from transformers import AutoTokenizer


# Load the RDF knowledge graph
def load_knowledge_graph(file_path):
    kg = rdflib.Graph()
    kg.parse(file_path, format=rdflib.util.guess_format(file_path))
    return kg

# Query the knowledge graph using SPARQL
def query_knowledge_graph(kg, query, use_fuzzy_matching=False, llm=None, tokenizer=None):
    context = ""

    if use_fuzzy_matching and llm and tokenizer:
        # Use LLM for fuzzy matching, generating possible triples
        input_text = f"Convert the following user query to RDF triples:\nUser query: '{query}'\nRDF triples:"
        input_ids = tokenizer.encode(input_text, return_tensors='pt')
        output = llm.generate(input_ids, max_length=100, num_beams=5, no_repeat_ngram_size=2, early_stopping=True)
        generated_triples = tokenizer.decode(output[0], skip_special_tokens=True)
        context = generated_triples
    else:
        # Use exact matching, execute SPARQL query
        sparql_query = f"""
        SELECT ?subject ?predicate ?object
        WHERE {{
            ?subject ?predicate ?object .
            FILTER(regex(str(?object), "{query}"))
        }} LIMIT 1
        """
        qres = kg.query(sparql_query)
        for row in qres:
            context = f"Subject: {row.subject}, Predicate: {row.predicate}, Object: {row.object}"
            break

    return context

# Generate an answer

def generate_answer(model, tokenizer, context, query, max_length=150):
    input_text = f"Question: {query}\nContext: {context}\nAnswer:"
    input_ids = tokenizer.encode(input_text, return_tensors='pt')
    output = model.generate(input_ids, max_length=max_length, num_return_sequences=1, num_beams=5,
                            no_repeat_ngram_size=2, early_stopping=True)
    return tokenizer.decode(output[0], skip_special_tokens=True)


# Specify the local path of the LLM
local_model_path = "C:/Users/6/.cache/huggingface/hub/models--TheBloke--Llama-2-7b-Chat-GGUF/snapshots/9ca625120374ddaae21f067cb006517d14dc91a6"

# Load the LLM from local path
model = AutoModelForCausalLM.from_pretrained(local_model_path, hf=True)

# 指定分词器文件所在的文件夹路径
local_tokenizer_path = "C:/Users/6/.cache/huggingface/hub/models--bert-base-uncased/snapshots/1dbc166cf8765166998eff31ade2eb64c8a40076"

# Load tokenizer from the model
tokenizer = AutoTokenizer.from_pretrained(local_tokenizer_path)




# Load your KG
kg_file_path = 'C:/Users/6/Desktop/ASKG_local_10_2024.ttl'  # Update to the actual path of your KG file
kg = load_knowledge_graph(kg_file_path)

# Process queries
queries = [
    'Using only the data provided in the knowledge graph, answer this question: In terms of knowledge graph completion, what are the key challenges in ensuring accuracy and completeness? Provide the answer in one paragraph.',
    # Add more queries as needed
]

for query in queries:
    # Find the relevant context from KG for the query
    context = query_knowledge_graph(kg, query, use_fuzzy_matching=False, llm=model, tokenizer=tokenizer)

    # Generate an answer based on the context
    answer = generate_answer(model, tokenizer, context, query)
    print(f"Query: {query}\nAnswer: {answer}\n")
