"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 11/3/2023 2:53 am
"""
import json
import os

from transformers import BartTokenizer, PegasusTokenizer
from transformers import BartForConditionalGeneration, PegasusForConditionalGeneration

if __name__ == "__main__":

    run_on = "ssh"

    if run_on == "local":
        input_path = "../../../ASKG_Paper_Dataset/keyword"
        output_dir = "../../../ASKG_Paper_Dataset/summarization"
    else:
        input_path = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/ASKG_Paper_Dataset/keyword"
        output_dir = "/home/users/u7274475/askg/anu-scholarly-kg/src/Papers/ASKG_Paper_Dataset/summarization"

    IS_CNNDM = True  # whether to use CNNDM dataset or XSum dataset
    LOWER = False

    print("***Begin Summarizing...***")

    # Load our model checkpoints
    if IS_CNNDM:
        model = BartForConditionalGeneration.from_pretrained('Yale-LILY/brio-cnndm-uncased')
        tokenizer = BartTokenizer.from_pretrained('Yale-LILY/brio-cnndm-uncased')
    else:
        model = PegasusForConditionalGeneration.from_pretrained('Yale-LILY/brio-xsum-cased')
        tokenizer = PegasusTokenizer.from_pretrained('Yale-LILY/brio-xsum-cased')

    max_length = 1024 if IS_CNNDM else 512

    for root, dirs, files in os.walk(input_path):
        for filename in files:
            file_path = os.path.join(input_path, filename)

            with open(file_path, "r") as f:
                json_data = json.load(f)

            # paper_data = {}
            key_list = list(json_data["sections"].keys())
            json_data["summarization"] = {}

            for i in range(len(key_list)):
                ARTICLE_TO_SUMMARIZE = json_data["sections"][key_list[i]]
                # generation example
                if LOWER:
                    article = ARTICLE_TO_SUMMARIZE.lower()
                else:
                    article = ARTICLE_TO_SUMMARIZE
                inputs = tokenizer([article], max_length=max_length, return_tensors="pt", truncation=True)
                # Generate Summary
                summary_ids = model.generate(inputs["input_ids"])

                s = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
                json_data["summarization"][key_list[i]] = s

            json_result = json.dumps(json_data)
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w') as f:
                f.write(json_result)
            print("complete:", filename)