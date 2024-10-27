import json
import os
import re
import subprocess
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
import json
from collections import defaultdict

def get_entities(text):
    """
    Extract meaningful entities from text with type information
    Returns: tuple (entities_list, is_entity_exist)
    """
    class Triples(BaseModel):
        head: str = Field(description="The subject or head entity in the triple")
        relation: str = Field(description="The relation or predicate connecting the head and tail entities")
        tail: str = Field(description="The object or tail entity in the triple")
        head_type: str = Field(description="The semantic type or category of the head entity")
        tail_type: str = Field(description="The semantic type or category of the tail entity")

    class Triples_list(BaseModel):
        triples: list[Triples] = Field(
            description="List of extracted triples, each containing head, relation, tail, and their types"
        )

    # Define meaningful entity types
    MEANINGFUL_TYPES = {
        # People and Organizations
        "Person", "Researcher", "Scientist", "Author",
        "Organization", "Institution", "University", "Company", "Research Group",

        # Academic Concepts
        "Algorithm", "Method", "Technique", "Framework", "Model",
        "Dataset", "Database", "Corpus",
        "Research Field", "Research Area", "Domain",
        "Theory", "Concept", "Paradigm",

        # Research Artifacts
        "Paper", "Publication", "Article", "Study",
        "Experiment", "Result", "Finding",
        "System", "Tool", "Software", "Platform",

        # Scientific Terms
        "Protein", "Gene", "Molecule", "Cell Type",
        "Disease", "Condition", "Symptom",
        "Technology", "Device", "Equipment",

        # Metrics and Measurements
        "Metric", "Measure", "Score", "Rate", "Index"
    }

    llm = ChatOpenAI(model="gpt-4o-mini")
    structured_llm = llm.with_structured_output(Triples_list)

    ans = structured_llm.invoke(
        f"""
        You are a knowledge graph building agent. 
        Extract triples from the following text, and identify the semantic types for the head and tail entities.
        Focus only on meaningful entities like persons, organizations, research concepts, methods, tools, datasets, etc.
        
        Text to analyze:
        {text}
        
        For each triple:
        - Separate the head, relation and tail
        - Classify the head and tail entities into their most specific semantic type from this list: {MEANINGFUL_TYPES}
        - Only include entities that can be clearly categorized into one of these types
        """
    )

    # Filter triples to only include those with meaningful entity types
    meaningful_triples = [
        triple for triple in ans.triples
        if triple.head_type in MEANINGFUL_TYPES or triple.tail_type in MEANINGFUL_TYPES
    ]

    return meaningful_triples, len(meaningful_triples) > 0