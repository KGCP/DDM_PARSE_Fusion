"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 28/11/2022 10:07 am
"""
import json
import os

from keybert import KeyBERT

if __name__ == "__main__":
    kw_model = KeyBERT()

    run_on = "ssh"

    if run_on == "local":
        input_path = "../../../ASKG_Paper_Dataset/splitted_papers"
        output_dir = "../../../ASKG_Paper_Dataset/keyword"
    else:
        input_path = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/ASKG_Paper_Dataset/splitted_papers"
        output_dir = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/ASKG_Paper_Dataset/keyword"

    print("***Begin Keyword Extracting...***")

    for root, dirs, files in os.walk(input_path):
        for filename in files:
            file_path = os.path.join(input_path, filename)

            with open(file_path, "r") as f:
                json_data = json.load(f)

            paper_data = {}
            paper_data["sections"] = json_data
            key_list = list(json_data.keys())
            paper_data["key_words"] = {}

            for i in range(len(key_list)):
                doc = json_data[key_list[i]]
                keywords = kw_model.extract_keywords(doc, keyphrase_ngram_range=(1, 3))
                paper_data["key_words"][key_list[i]] = keywords

            json_result = json.dumps(paper_data)
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w') as f:
                f.write(json_result)
            print("complete:", filename)

    print("complete all!")

