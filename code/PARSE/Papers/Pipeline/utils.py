import json
import os
import re
import subprocess
from pydantic import BaseModel, Field
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
        relation: str = Field(
            description="The relation or predicate connecting the head and tail entities"
        )
        tail: str = Field(description="The object or tail entity in the triple")
        head_type: str = Field(
            description="The semantic type or category of the head entity"
        )
        tail_type: str = Field(
            description="The semantic type or category of the tail entity"
        )

    class Triples_list(BaseModel):
        triples: list[Triples] = Field(
            description="List of extracted triples, each containing head, relation, tail, and their types"
        )

    # Define meaningful entity types
    MEANINGFUL_TYPES = {
        # People and Organizations
        "Person",
        "Researcher",
        "Scientist",
        "Author",
        "Organization",
        "Institution",
        "University",
        "Company",
        "Research Group",
        # Academic Concepts
        "Algorithm",
        "Method",
        "Technique",
        "Framework",
        "Model",
        "Dataset",
        "Database",
        "Corpus",
        "Research Field",
        "Research Area",
        "Domain",
        "Theory",
        "Concept",
        "Paradigm",
        # Research Artifacts
        "Paper",
        "Publication",
        "Article",
        "Study",
        "Experiment",
        "Result",
        "Finding",
        "System",
        "Tool",
        "Software",
        "Platform",
        # Scientific Terms
        "Protein",
        "Gene",
        "Molecule",
        "Cell Type",
        "Disease",
        "Condition",
        "Symptom",
        "Technology",
        "Device",
        "Equipment",
        # Metrics and Measurements
        "Metric",
        "Measure",
        "Score",
        "Rate",
        "Index",
    }

    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0, max_retries=3)
    structured_llm = llm.with_structured_output(Triples_list)

    prompt = f"""
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

    try:
        ans = structured_llm.invoke(prompt)
        candidates = ans.triples
    except Exception:
        # Fallback to JSON output parsing if structured output validation fails
        raw_json_llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0, max_retries=3)
        json_prompt = f"""
            Extract triples strictly in this JSON format:
            {{"triples":[{{"head":"...","relation":"...","tail":"...","head_type":"...","tail_type":"..."}}]}}
            Use only types from this set: {MEANINGFUL_TYPES}
            If none, return {{"triples":[]}}.

            Text:
            {text}
        """
        raw = raw_json_llm.invoke(json_prompt)
        # raw can be a BaseMessage; get content
        content = getattr(raw, "content", str(raw))
        try:
            data = json.loads(content)
            triples = data.get("triples", []) if isinstance(data, dict) else []
        except Exception:
            triples = []
        candidates = []
        for t in triples:
            head = (t or {}).get("head")
            rel = (t or {}).get("relation")
            tail = (t or {}).get("tail")
            htype = (t or {}).get("head_type")
            ttype = (t or {}).get("tail_type")
            if not all([head, rel, tail, htype, ttype]):
                continue
            # Construct a pydantic Triples instance for consistent return type
            try:
                candidates.append(Triples(head=head, relation=rel, tail=tail, head_type=htype, tail_type=ttype))
            except Exception:
                continue

    # Filter triples to only include those with meaningful entity types
    meaningful_triples = [
        triple
        for triple in candidates
        if triple.head_type in MEANINGFUL_TYPES or triple.tail_type in MEANINGFUL_TYPES
    ]

    return meaningful_triples, len(meaningful_triples) > 0
