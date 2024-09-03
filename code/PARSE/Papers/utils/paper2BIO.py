"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 3/10/2022 4:39 pm

This file will download paper raw text from http://rsmsrv01.nci.org.au:5000/ANU-Scholarly-KG/_MEL_TNNT_output_researchers-data-papers-2022
and tokenize to BIO file
"""
import json
import os.path
import re
import requests
import io
import sys
import spacy
import contextlib
from pandas import DataFrame

with contextlib.redirect_stdout(io.StringIO()):
    spacy.cli.download('en_core_web_md', False, False, '--quiet')
    spacy_nlp = spacy.load(
        'en_core_web_md', disable=['tokenizer', 'tagger', 'ner', 'textcat', 'lemmatizer']
    )

def get_paper_list():
    paperlist_path = "paperlist.txt"
    paper_list = []
    with open(paperlist_path) as paperlist_file:
        for line in paperlist_file.readlines():
            paper_list.append(line.strip())
    return paper_list


def get_paper(paper):
    askg_dir = f"http://rsmsrv01.nci.org.au:5000/ANU-Scholarly-KG/_MEL_TNNT_output_researchers-data-papers-2022/{paper}/MEL+NER_output/clean-text"
    headers = {
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }
    r = requests.get(askg_dir)
    raw_text = str(r.content)
    return raw_text


def clean_paper(raw_text, paper_name):
    document = spacy_nlp(raw_text)
    clean_text = []
    for span in document.sents:
        sentence = [document[i] for i in range(span.start, span.end)]
        for token in sentence:
            token = str(token)
            if '\\\\n' in token:
                word = token.split('\\\\n')
                # word = list(reversed(word))
                for w in word:
                    if w != "" and w != "PSPACE":
                        clean_text.append(w)
            elif token == "PSPACE":
                continue
            # elif '.' in token:
            #     word = token.split('.')
            #     for w in word:
            #         if w != "":
            #             clean_text.append(w.lower())
            #         else:
            #             clean_text.append(".")
            # elif ',' in token:
            #     word = token.split(',')
            #     for w in word:
            #         if w != "":
            #             clean_text.append(w.lower())
            #         else:
            #             clean_text.append(".")
            elif "=" in token:
                continue
            # elif any(symbol in token for symbol in ["/", ";", ":", "[", "]", "{", "}", "(", ")", "#", "$", "%", "&", "*", "-", "|"]):
            #     pattern = '[a-zA-Z]+'
            #     result = re.findall(pattern, token)
            #     for item in result:
            #         # if len(item) <= 1:
            #         #     continue
            #         clean_text.append(item.lower())
            else:
                clean_text.append(token)

    df_dict = {
        "text": clean_text,
        "label": ["O"] * len(clean_text)
    }
    df = DataFrame(data=df_dict)
    output_path = "../ASKG_Paper_Dataset/BIO_Format"
    paper_name = paper_name[:-4] + ".csv"
    df.to_csv(os.path.join(output_path, paper_name), index=False, sep='\t')

def get_cs_paper_list():
    paper_dict_path = "../../Papers/ASKG_Paper_Dataset/paper_info/paper_info.json"
    paper_info = {}
    with open(paper_dict_path) as json_f:
        paper_info = json.load(json_f)
    cs_paper_list = []
    cs_ai_paper_list = []
    cs_cl_paper_list = []
    for key in paper_info.keys():
        for subkey in paper_info[key].keys():
            if subkey == "cs":
                cs_paper_list.append(key + ".pdf")
                if 'AI' in paper_info[key][subkey]:
                    cs_ai_paper_list.append(key+".pdf")
                if 'CL' in paper_info[key][subkey]:
                    cs_cl_paper_list.append(key+".pdf")
    return cs_paper_list, cs_ai_paper_list, cs_cl_paper_list


def save_raw_text(paper, raw_text):
    save_dir = "../ASKG_Paper_Dataset/RawText"
    paper = re.sub(r"\.pdf$", "", paper)
    save_path = os.path.join(save_dir, paper + ".txt")
    with open(save_path, "w") as f:
        f.write(raw_text)

if __name__ == '__main__':
    paper_list = get_paper_list()
    cs_paper_list, cs_ai_paper_list, cs_cl_paper_list = get_cs_paper_list()

    for paper in cs_paper_list:
        if paper in cs_paper_list:
            raw_text = get_paper(paper)
            save_raw_text(paper, raw_text)
            clean_paper(raw_text, paper_name=paper)
