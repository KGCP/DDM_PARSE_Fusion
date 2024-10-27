import json
import os
import re
import subprocess
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
import json
from collections import defaultdict

def get_entities(text):

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

    llm = ChatOpenAI(model="gpt-4o")
    structured_llm = llm.with_structured_output(Triples_list)

    result_list = []

    ans = structured_llm.invoke(
        f"""
        You are a knowledge graph building agent. 
        Extract triples from the following text, and identify the semantic types for the head and tail entities:

        {text}
        
        For each triple:
        - Separate the head, relation and tail
        - Classify the head and tail entities into their most specific semantic type
        """
    )

    triples_list = ans.triples


    triples_dict_list = [triple.model_dump() for triple in triples_list]

    with open('triples.json', 'w') as f:
        json.dump(triples_dict_list, f, indent=2)

    return ans.triples

text = """
IFI16 and cGAS Are both Expressed in Normal Human Cells. To define the relative roles of cGAS and IFI16 in innate sensing in a single cell type, we wished to define human cells that expressed both of these proteins. We therefore initially examined the basal levels of cGAS protein in normal human foreskin fibroblasts (HFFs),
a normal oral keratinocyte (NOK) cell line immortalized with human telomerase reverse transcriptase (16), HEK293 cells, and HEK293T cells. cGAS protein was detectable in both HFF and NOK cells but not in HEK293 or HEK293T cells (Fig. 1A), the latter as reported previously (11, 12). Consistent with this observation, we detected markedly higher cGAS RNA levels in HFF and NOK cells compared with HEK293 or HEK293T cells (Fig. 1C). Surprisingly, although cGAS has been described as a cytosolic protein (11, 12), using cellular fractionation we found that human cGAS was localized in both the nucleus and the cytoplasm of HFF and NOK cells (Fig. 1B). The subcellular distribution of cGAS in HFF and NOK cells was confirmed by confocal immunofluoresence microscopy (Fig. S1A). Immunofluorescence analysis of cells depleted for cGAS or IFI16 showed reduced signal for the depleted proteins, showing the specificities of the antibodies (Fig. S1B). Interestingly, human cGAS
appeared to be mainly nuclear upon stable ectopic expression in HEK293 cells (Fig. S1B). We found that IFI16 was also expressed in HFF and NOK cells, although the IFI16 isoforms in NOK cells appeared to run at a higher apparent molecular weight than those in HFF (Fig. 1A). Furthermore, the innate immune response to HSV-1 infection at 6 h postinfection (hpi)
was greater in HFF cells than in NOKs or HEK293 cells (Fig.

1D). Based on the robust induction of IFNβ RNA in HSV-1–
infected HFFs observed above and previous reports that HFFs are competent for IFI16 activity (7, 8, 17), we chose HFF cells to study the relative contributions of cGAS and IFI16 to the innate immune response to foreign DNA.
"""

get_entities(text)

