"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 25/10/2022 7:47 pm
"""
import json
import os

import requests
import nltk
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import wordnet

cache_file = '/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/Models/models/nel_models/cache.json'
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        cached_requests = json.load(f)
else:
    cached_requests = {}


stopwords = set(nltk.corpus.stopwords.words("english"))
def do_remove_stopwords(entity):
    tokens = entity.split()
    result = ""
    for t in tokens:
        if t not in stopwords:
            t = t.strip()
            t = t.strip('.,()!@#$%^&*/')
            result += t
            result += " "
    result = result.strip(" ")
    return result


def lemmatize(entity):
    result = ""
    wnl = WordNetLemmatizer()
    toks = entity.split()
    for t in toks:
        t = t.lower()
        pos = None
        tok_tag = pos_tag([t])[0]

        # ignore stopwords
        if t in stopwords or t.lower() in stopwords:
                continue
        else:
            # for better lemmatizing results, the word class is required
            if tok_tag[1].startswith('J'):
                pos = wordnet.ADJ
            elif tok_tag[1].startswith('V'):
                pos = wordnet.VERB
            elif tok_tag[1].startswith('N'):
                pos = wordnet.NOUN
            elif tok_tag[1].startswith('R'):
                pos = wordnet.ADV

        wordnet_pos = pos if pos != None else wordnet.NOUN
        t = wnl.lemmatize(t, pos=wordnet_pos)
        result += t
        result += " "
    result = result.strip()

    return result


def check_exact_match(raw_text, entity, ner_dict, c, key):
    exact_match = False
    all_match_list = []
    wiki_res_dict = None
    try:
        wiki_res_dict = json.loads(raw_text)
    except:
        pass
    else:
        if wiki_res_dict is not None:
            # wiki_res_dict = json.loads(raw_text)
            exact_match_list = []
            all_match_list = []
            index = 0
            for item in wiki_res_dict['search']:
                if entity == item['label'].lower():
                    exact_match_list.append(index)
                all_match_list.append(index)
                index += 1
            if len(exact_match_list) == 1:
                exact_match = True
                idx = exact_match_list[0]
                ner_dict[c][key]["wikidata_ID"] = wiki_res_dict['search'][idx]['id']
                ner_dict[c][key]["is_matched"] = True
                ner_dict[c][key]["exact_match"] = True
                try:
                    ner_dict[c][key]["wikidata_desc"] = wiki_res_dict['search'][idx]['description']
                    ner_dict[c][key]["matched_words"] = entity
                except:
                    pass
            elif len(exact_match_list) > 1:
                exact_match = True
                idx = exact_match_list[0]
                ner_dict[c][key]["wikidata_ID"] = wiki_res_dict['search'][idx]['id']
                ner_dict[c][key]["is_matched"] = True
                ner_dict[c][key]["exact_match"] = True
                try:
                    ner_dict[c][key]["wikidata_desc"] = wiki_res_dict['search'][idx]['description']
                    ner_dict[c][key]["matched_words"] = entity
                except:
                    pass
    return exact_match, all_match_list, wiki_res_dict


def getWikidata(ner_dict, mode, remove_stopwords, try_lemmatize, min_length, max_length, filename):
    output_path = f"/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/ASKG_Paper_Dataset/NEL_result/{filename}"
    all_match_list1 = []
    all_match_list2 = []
    wiki_res_dict1 = {}
    wiki_res_dict2 = {}
    entity_change_dict = {}
    for c in ner_dict.keys():
        for key in ner_dict[c]:
            ner_dict[c][key]["is_matched"] = False
            ner_dict[c][key]["exact_match"] = False
            entity = key.lower()

            # Skip entities with only one word
            if ' ' not in entity:
                continue

            raw_text = request_wiki(entity)
            exact_match, all_match_list, wiki_res_dict = check_exact_match(raw_text, entity, ner_dict, c, key)

            new_entity = entity
            if remove_stopwords and not exact_match:
                new_entity = do_remove_stopwords(entity)
                entity_change_dict[entity] = [c, new_entity]
                raw_text = request_wiki(new_entity)
                exact_match, all_match_list1, wiki_res_dict1 = check_exact_match(raw_text, new_entity, ner_dict, c, key)
            if try_lemmatize and not exact_match:
                new_entity = lemmatize(new_entity)
                entity_change_dict[entity] = [c, new_entity]
                raw_text = request_wiki(new_entity)
                exact_match, all_match_list2, wiki_res_dict2 = check_exact_match(raw_text, new_entity, ner_dict, c, key)

            if not exact_match:
                if len(all_match_list) > 0:
                    idx = all_match_list[0]
                    ner_dict[c][key]["wikidata_ID"] = wiki_res_dict['search'][idx]['id']
                    ner_dict[c][key]["exact_match"] = False
                    ner_dict[c][key]["matched_words"] = wiki_res_dict['search'][idx]['label']
                    ner_dict[c][key]["is_matched"] = True
                    try:
                        ner_dict[c][key]["wikidata_desc"] = wiki_res_dict['search'][idx]['description']
                    except:
                        pass
                elif len(all_match_list1) > 0:
                    idx = all_match_list1[0]
                    ner_dict[c][key]["wikidata_ID"] = wiki_res_dict1['search'][idx]['id']
                    ner_dict[c][key]["exact_match"] = False
                    ner_dict[c][key]["matched_words"] = wiki_res_dict1['search'][idx]['label']
                    ner_dict[c][key]["is_matched"] = True
                    try:
                        ner_dict[c][key]["wikidata_desc"] = wiki_res_dict1['search'][idx]['description']
                    except:
                        pass
                elif len(all_match_list2) > 0:
                    idx = all_match_list2[0]
                    ner_dict[c][key]["wikidata_ID"] = wiki_res_dict2['search'][idx]['id']
                    ner_dict[c][key]["exact_match"] = False
                    ner_dict[c][key]["matched_words"] = wiki_res_dict2['search'][idx]['label']
                    ner_dict[c][key]["is_matched"] = True
                    try:
                        ner_dict[c][key]["wikidata_desc"] = wiki_res_dict2['search'][idx]['description']
                    except:
                        pass

    for key in entity_change_dict.keys():
        c = entity_change_dict[key][0]
        new_en = entity_change_dict[key][1]
        ner_dict[c][new_en] = ner_dict[c].pop(key)

    reserve_key = []
    for c in ner_dict.keys():
        for key in ner_dict[c]:
            if mode == "fuzzy_match":
                if ner_dict[c][key]["is_matched"] == True:
                    reserve_key.append(key)
                    # if not any(x in ner_dict[c][key]["wikidata_desc"].lower() for x in["article", "thesis"]):
                    #     reserve_key.append(key)
            elif mode == "all":
                reserve_key.append(key)
            elif mode == "exact_match":
                if ner_dict[c][key]["exact_match"] == True:
                    reserve_key.append(key)

    reserve_key = [x for x in reserve_key if len(x.split()) <= max_length and len(x.split()) >= min_length]
    for c in list(ner_dict.keys()):
        for key in list(ner_dict[c].keys()):
            if key not in reserve_key:
                del ner_dict[c][key]

    with open(output_path, "w") as f:
        json.dump(ner_dict, f)


def request_wiki(entity):
    print(entity)
    if entity in cached_requests:
        return cached_requests[entity]

    wiki_url = f'https://www.wikidata.org/w/api.php?action=wbsearchentities&search={entity}&language=en&limit=20&format=json'
    r = requests.get(wiki_url)
    raw_text = str(r.content)[2:-1]

    # Save the request result to the cache
    cached_requests[entity] = raw_text
    return raw_text


if __name__ == '__main__':
    path = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/ASKG_Paper_Dataset/NER_result"
    mode = "all"
    remove_stopwords = True
    try_lemmatize = True
    min_length = 2
    max_length = 4

    for filename in os.listdir(path):
        print(filename)
        if filename.endswith('.json'):
            file_path = os.path.join(path, filename)
            with open(file_path, 'r') as file:
                ner_result = json.load(file)
            getWikidata(ner_result, mode, remove_stopwords, try_lemmatize, min_length, max_length, filename)

            with open(cache_file, 'w') as f:
                json.dump(cached_requests, f)