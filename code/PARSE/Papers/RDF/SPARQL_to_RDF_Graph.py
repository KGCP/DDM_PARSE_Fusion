import csv
import hashlib

import pandas as pd
import requests
import rdflib
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef, XSD, OWL, SKOS, DC, RDFS
import json
from urllib.parse import quote
import re

old_ASKG = Graph()
ASKG_namespace_onto = Namespace("https://www.anu.edu.au/onto/scholarly#")
ASKG_namespace_data = Namespace("https://www.anu.edu.au/onto/scholarly/")
DOMO_namespace = Namespace("https://www.anu.edu.au/onto/domo#")
WIKIDATA_namespace = Namespace("http://www.wikidata.org/entity/")
TNNT_namespace = Namespace("https://soco.cecc.anu.edu.au/tool/TNNT#")
agrif_md_namespace = Namespace("http://linked.data.gov.au/def/agrif-metadata#")
old_ASKG.bind("askg-onto", ASKG_namespace_onto)
old_ASKG.bind("askg-data", ASKG_namespace_data)
old_ASKG.bind("domo", DOMO_namespace)
old_ASKG.bind("wd", WIKIDATA_namespace)
old_ASKG.bind("skos", SKOS)
old_ASKG.bind("dc", DC)
old_ASKG.bind("tnnt", TNNT_namespace)
old_ASKG.bind("agrif-md", agrif_md_namespace)

def blake2s_hash(input_string, digest_size=7):
    input_bytes = input_string.encode('utf-8')
    hasher = hashlib.blake2s(digest_size=digest_size)
    hasher.update(input_bytes)
    hash_result = hasher.digest()
    return hash_result.hex()

def save_json():
    endpoint = "http://rsmdb01.nci.org.au:8890/sparql"

    query = """
    PREFIX : <https://www.anu.edu.au/onto/scholarly/kg#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX mag: <https://makg.org/property/>
    PREFIX org: <http://www.w3.org/ns/org#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX tco: <https://w3id.org/scholarlydata/ontology/conference-ontology.owl#>
    PREFIX xml: <http://www.w3.org/XML/1998/namespace>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX vann: <http://purl.org/vocab/vann/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX agrif-md: <http://linked.data.gov.au/def/agrif-metadata#>
    PREFIX anu-kg-v1: <https://www.anu.edu.au/data/scholarly/kg/v1>

    SELECT ?subject ?predicate ?object
    WHERE {
      ?subject ?predicate ?object .
    }
    """

    params = {
        "default-graph-uri": "https://www.anu.edu.au/data/scholarly/kg/v1",
        "query": query,
        "should-sponge": "",
        "format": "application/json",
        "timeout": 0,
        "debug": "on",
        "run": " Run Query ",
    }

    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        print("request success！")
        json_response = response.json()
        with open("anu-kg-v1.json", "w") as f:
            json.dump(json_response, f)


def construct_rdf():

    df = pd.read_csv('result_csv.csv')
    rows_to_drop = []


    for index, row in df.iterrows():
        s_value = row['s']
        p_value = row['p']
        o_value = row['o']

        if ("https://www.anu.edu.au/onto/scholarly/kg#Author" in s_value) and ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in p_value) and ("https://www.anu.edu.au/onto/scholarly/kg#Author" in o_value):

            rows_to_drop.append(index)

            author_name = row['s']
            pattern = r'https:\/\/www\.anu\.edu\.au\/onto\/scholarly\/kg#Author-([\w-]+)'
            match = re.search(pattern, author_name)
            if match:
                author_name = match.group(1).replace('-', ' ')
            else:
                continue
            author_label_str = f"{author_name}"
            author_label = Literal(author_label_str, lang="en")
            author_hashed = blake2s_hash(author_label_str)
            author_entity = ASKG_namespace_data[f"Author-{author_hashed}"]
            if (author_entity, RDF.type, ASKG_namespace_onto.Author) not in old_ASKG:
                old_ASKG.add((author_entity, RDF.type, ASKG_namespace_onto.Author))
                old_ASKG.add((author_entity, RDFS.label, author_label))


        if ("https://www.anu.edu.au/onto/scholarly/kg#Researcher" in s_value) and (
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in p_value) and (
                "https://www.anu.edu.au/onto/scholarly/kg#Researcher" in o_value):

            rows_to_drop.append(index)

            researcher_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#Researcher-")
            title_with_hyphens = researcher_name[prefix_length:]
            researcher_name = title_with_hyphens.replace('-', ' ')

            researcher_label_str = f"{researcher_name}"
            researcher_label = Literal(researcher_label_str, lang="en")
            researcher_hashed = blake2s_hash(researcher_label_str)
            researcher_entity = ASKG_namespace_data[f"Researcher-{researcher_hashed}"]
            if (researcher_entity, RDF.type, ASKG_namespace_onto.Researcher) not in old_ASKG:
                old_ASKG.add((researcher_entity, RDF.type, ASKG_namespace_onto.Researcher))
                old_ASKG.add((researcher_entity, RDFS.label, researcher_label))

        #paper_entity is askg.Paper
        if ("https://www.anu.edu.au/onto/scholarly/kg#Paper" in s_value) and ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in p_value) and ("https://www.anu.edu.au/onto/scholarly/kg#Paper" in o_value):

            rows_to_drop.append(index)

            paper_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#Paper-")
            title_with_hyphens = paper_name[prefix_length:]
            paper_name = title_with_hyphens.replace('-', ' ')

            paper_label_str = f"{paper_name}"
            paper_hashed = blake2s_hash(paper_label_str)
            paper_label = Literal(paper_label_str, lang="en")
            paper_entity = ASKG_namespace_data[f"Paper-{paper_hashed}"]
            if (paper_entity, RDF.type, ASKG_namespace_onto.Paper) not in old_ASKG:
                old_ASKG.add((paper_entity, RDF.type, ASKG_namespace_onto.Paper))
                old_ASKG.add((paper_entity, RDFS.label, paper_label))

        #Conference
        if ("https://www.anu.edu.au/onto/scholarly/kg#Conference" in s_value) and ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in p_value) and ("https://www.anu.edu.au/onto/scholarly/kg#Conference" in o_value):

            rows_to_drop.append(index)

            conf_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#Conference-")
            conf = conf_name[prefix_length:]

            conf_label_str = f"{conf}"
            conf_hashed = blake2s_hash(conf_label_str)
            conf_label = Literal(conf_label_str, lang="en")
            conf_entity = ASKG_namespace_data[f"Conference-{conf_hashed}"]
            if (conf_entity, RDF.type, ASKG_namespace_onto.Conference) not in old_ASKG:
                old_ASKG.add((conf_entity, RDF.type, ASKG_namespace_onto.Conference))
                old_ASKG.add((conf_entity, RDFS.label, conf_label))

        #Journal
        if ("https://www.anu.edu.au/onto/scholarly/kg#Journal" in s_value) and ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in p_value) and ("https://www.anu.edu.au/onto/scholarly/kg#Journal" in o_value):

            rows_to_drop.append(index)

            journal_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#Journal-")
            title_with_hyphens = journal_name[prefix_length:]
            journal_name = title_with_hyphens.replace('-', ' ')

            journal_label_str = f"{journal_name}"
            journal_label = Literal(journal_label_str, lang="en")
            journal_hashed = blake2s_hash(journal_label_str)
            journal_entity = ASKG_namespace_data[f"Journal-{journal_hashed}"]
            if (journal_entity, RDF.type, ASKG_namespace_onto.Journal) not in old_ASKG:
                old_ASKG.add((journal_entity, RDF.type, ASKG_namespace_onto.Journal))
                old_ASKG.add((journal_entity, RDFS.label, journal_label))


        # DigitalArtefact is askg.DigitalArtefact
        if ("https://www.anu.edu.au/onto/scholarly/kg#DigitalArtefact" in s_value) and ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in p_value) and ("http://linked.data.gov.au/def/agrif#DigitalArtefact" in o_value):

            rows_to_drop.append(index)

            DA_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#DigitalArtefact-")
            title_with_hyphens = DA_name[prefix_length:]
            DA_name = title_with_hyphens.replace('-', ' ')

            DA_label_str = f"{DA_name}"
            DA_label = Literal(DA_label_str, lang="en")
            DA_entity = ASKG_namespace_data[f"DigitalArtefact-{DA_name}"]
            if (DA_entity, RDF.type, agrif_md_namespace.Paper) not in old_ASKG:
                old_ASKG.add((DA_entity, RDF.type, agrif_md_namespace.DigitalArtefact))
                old_ASKG.add((DA_entity, RDFS.label, DA_label))


        if ("https://www.anu.edu.au/onto/scholarly/kg#Record" in s_value) and ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in p_value) and ("http://linked.data.gov.au/def/agrif#Record" in o_value):

            rows_to_drop.append(index)

            record_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#Record-")
            title_with_hyphens = record_name[prefix_length:]
            record_name = title_with_hyphens.replace('-', ' ')

            record_label_str = f"{record_name}"
            record_label = Literal(record_label_str, lang="en")
            record_entity = ASKG_namespace_data[f"Record-{record_name}"]
            if (record_entity, RDF.type, agrif_md_namespace.Record) not in old_ASKG:
                old_ASKG.add((record_entity, RDF.type, agrif_md_namespace.Record))
                old_ASKG.add((record_entity, RDFS.label, record_label))


        if ("https://www.anu.edu.au/onto/scholarly/kg#CreationEventForDoc" in s_value) and ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in p_value) and ("http://linked.data.gov.au/def/agrif#CreationEvent" in o_value):

            rows_to_drop.append(index)

            CED_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#CreationEventForDoc-")
            title_with_hyphens = CED_name[prefix_length:]
            CED_name = title_with_hyphens.replace('-', ' ')

            CED_entity = ASKG_namespace_data[f"CreationEventForDoc-{CED_name}"]
            if (CED_entity, RDF.type, agrif_md_namespace.CreationEventForDoc) not in old_ASKG:
                old_ASKG.add((CED_entity, RDF.type, agrif_md_namespace.CreationEventForDoc))

        if ("https://www.anu.edu.au/onto/scholarly/kg#CreationEventForDoc" in s_value) and (
                "http://www.w3.org/2000/01/rdf-schema#label" in p_value):

            rows_to_drop.append(index)

            CED_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#CreationEventForDoc-")
            title_with_hyphens = CED_name[prefix_length:]
            CED_name = title_with_hyphens.replace('-', ' ')

            CED_entity = ASKG_namespace_data[f"CreationEventForDoc-{CED_name}"]
            if (CED_entity, RDF.type, agrif_md_namespace.CreationEventForDoc) not in old_ASKG:
                old_ASKG.add((CED_entity, RDF.type, agrif_md_namespace.CreationEventForDoc))

            label_str = row['o']
            label = Literal(label_str, lang="en")
            old_ASKG.add((CED_entity, RDFS.label, label))

        if ("https://www.anu.edu.au/onto/scholarly/kg#Paper" in s_value) and ("https://www.anu.edu.au/onto/scholarly/kg#hasAuthor" in p_value) and ("https://www.anu.edu.au/onto/scholarly/kg#Author" in o_value):

            rows_to_drop.append(index)

            paper_name = row['s']
            paper_prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#Paper-")
            title_with_hyphens = paper_name[paper_prefix_length:]
            paper_name = title_with_hyphens.replace('-', ' ')

            author_name = row['o']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#Author-")
            name_with_hyphens = author_name[prefix_length:]
            author_name = name_with_hyphens.replace('-', ' ')
            author_label_str = f"{author_name}"
            author_label = Literal(author_label_str, lang="en")
            author_hashed = blake2s_hash(author_label_str)
            author_entity = ASKG_namespace_data[f"Author-{author_hashed}"]

            paper_label_str = f"{paper_name}"
            paper_label = Literal(paper_label_str, lang="en")
            paper_hashed = blake2s_hash(paper_label_str)
            paper_entity = ASKG_namespace_data[f"Paper-{paper_hashed}"]
            if (paper_entity, RDF.type, ASKG_namespace_onto.Paper) not in old_ASKG:
                old_ASKG.add((paper_entity, RDF.type, ASKG_namespace_onto.Paper))
                old_ASKG.add((paper_entity, RDFS.label, paper_label))

            if (author_entity, RDF.type, ASKG_namespace_onto.Author) not in old_ASKG:
                old_ASKG.add((author_entity, RDF.type, ASKG_namespace_onto.Author))
                old_ASKG.add((author_entity, RDFS.label, author_label))

            if (paper_entity, ASKG_namespace_onto.hasAuthor, author_entity) not in old_ASKG:
                old_ASKG.add((paper_entity, ASKG_namespace_onto.hasAuthor, author_entity))


        if ("https://www.anu.edu.au/onto/scholarly/kg#AreaOfExpertise" in s_value) and ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in p_value) and ("https://www.anu.edu.au/onto/scholarly/kg#AreaOfExpertise" in o_value):

            rows_to_drop.append(index)

            AOE_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#AreaOfExpertise-")
            AOE_h = AOE_name[prefix_length:]
            AOE_label_str = f"{AOE_h}"
            AOE_label = Literal(AOE_label_str, lang="en")
            AOE_hashed= blake2s_hash(AOE_label_str)

            AOE_entity = ASKG_namespace_data[f"AreaOfExpertise-{AOE_hashed}"]
            if (AOE_entity, RDF.type, ASKG_namespace_onto.AreaOfExpertise) not in old_ASKG:
                old_ASKG.add((AOE_entity, RDF.type, ASKG_namespace_onto.AreaOfExpertise))
                old_ASKG.add((AOE_entity, RDFS.label, AOE_label))

        #hasAreaOfExpertise
        if ("https://www.anu.edu.au/onto/scholarly/kg#Researcher" in s_value) and ("https://www.anu.edu.au/onto/scholarly/kg#hasAreaOfExpertise" in p_value) and ("https://www.anu.edu.au/onto/scholarly/kg#AreaOfExpertise" in o_value):

            rows_to_drop.append(index)

            AOE_name = row['o']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#AreaOfExpertise-")
            AOE_h = AOE_name[prefix_length:]
            AOE_label_str = f"{AOE_h}"
            AOE_label = Literal(AOE_label_str, lang="en")
            AOE_hashed= blake2s_hash(AOE_label_str)

            AOE_entity = ASKG_namespace_data[f"AreaOfExpertise-{AOE_hashed}"]
            if (AOE_entity, RDF.type, ASKG_namespace_onto.AreaOfExpertise) not in old_ASKG:
                old_ASKG.add((AOE_entity, RDF.type, ASKG_namespace_onto.AreaOfExpertise))
                old_ASKG.add((AOE_entity, RDFS.label, AOE_label))

            researcher_name = row['s']
            prefix_length = len("https://www.anu.edu.au/onto/scholarly/kg#Researcher-")
            title_with_hyphens = researcher_name[prefix_length:]
            researcher_name = title_with_hyphens.replace('-', ' ')

            researcher_label_str = f"{researcher_name}"
            researcher_label = Literal(researcher_label_str, lang="en")
            researcher_hashed = blake2s_hash(researcher_label_str)
            researcher_entity = ASKG_namespace_data[f"Researcher-{researcher_hashed}"]
            if (researcher_entity, RDF.type, ASKG_namespace_onto.Researcher) not in old_ASKG:
                old_ASKG.add((researcher_entity, RDF.type, ASKG_namespace_onto.Researcher))
                old_ASKG.add((researcher_entity, RDFS.label, researcher_label))

            if (researcher_entity, ASKG_namespace_onto.hasAreaOfExpertise, AOE_entity) not in old_ASKG:
                old_ASKG.add((researcher_entity, ASKG_namespace_onto.hasAreaOfExpertise, AOE_entity))



        #clean csv
        if ("https://www.anu.edu.au/onto/scholarly/kg#Author" in s_value) and ("http://www.w3.org/2000/01/rdf-schema#label" in p_value):

            rows_to_drop.append(index)

        if ("https://www.anu.edu.au/onto/scholarly/kg#Researcher" in s_value) and ("http://www.w3.org/2000/01/rdf-schema#label" in p_value):

            rows_to_drop.append(index)

        if ("https://www.anu.edu.au/onto/scholarly/kg#Record" in s_value) and ("http://www.w3.org/2000/01/rdf-schema#label" in p_value):

            rows_to_drop.append(index)

        if ("https://www.anu.edu.au/onto/scholarly/kg#DigitalArtefact" in s_value) and ("http://www.w3.org/2000/01/rdf-schema#label" in p_value):

            rows_to_drop.append(index)

    old_ASKG.serialize(destination='Old_ASKG.ttl', format='turtle')

    df = df.drop(rows_to_drop)

    df.reset_index(drop=True, inplace=True)
    df.to_csv('processed_csv_v1.csv', index=False)



if __name__ == "__main__":
    construct_rdf()
