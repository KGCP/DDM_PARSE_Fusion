"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/3/2023 11:45 pm
"""
import json
import os
import re

def split_position(keywords_pos):
    value_list = list(keywords_pos.values())

    #verify the list in case the later part index is larger than the previous part
    prev_value = 0
    for i in range(len(value_list)):
        if value_list[i] != -1 and value_list[i] < prev_value:
            value_list[i] = -1
        elif value_list != -1 and value_list[i] > prev_value:
            prev_value = value_list[i]

    left_pos = 0
    right_pos = 0
    while left_pos < len(value_list):
        while value_list[right_pos] == -1 and right_pos < len(value_list):
            right_pos += 1
        if right_pos > left_pos:
            pos_diff = right_pos - left_pos + 1
            interval = (value_list[right_pos] - value_list[left_pos - 1]) / pos_diff
            for i in range(right_pos - left_pos):
                t= value_list[left_pos - i]
                value_list[left_pos + i] = int(value_list[left_pos - 1] + interval * (i + 1))
            left_pos = right_pos
        right_pos += 1
        left_pos += 1

        for i, key in enumerate(keywords_pos.keys()):
            keywords_pos[key] = value_list[i]

if __name__ == "__main__":
    file_path = "../../ASKG_Paper_Dataset/RawText"
    output_dir = "../../ASKG_Paper_Dataset/splitted_papers"

    for root, dirs, files in os.walk(file_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            with open(file_path, "r") as f:
                content = f.read()

            sections = {"Abstract": ""}
            keywords_pos = {}
            keywords = {
                "Introduction": ["Introduction"],
                "Related Work": ["Related Work", "Literature Review", "Background"],
                "Methodology": ["Method", "Methodology"],
                "Experiment": ["Experiment", "Result", "Evaluation"],
                "Discussion": ["Discussion", "Conclusion", "Conclusions", "Conclusion and Discussion"]
            }

            keywords_pos["start"] = 0
            for key in keywords.keys():
                sections[key] = ""
                keywords_pos[key] = -1
            keywords_pos["end"] = len(content)

            for key in keywords.keys():
                for item in keywords[key]:
                    index = content.find(item)
                    if index != -1:
                        keywords_pos[key] = index
                        break

            split_position(keywords_pos)

            pos_list= list(keywords_pos.values())
            key_list = list(sections.keys())
            assert len(key_list) == len(pos_list) - 1
            for i in range(len(pos_list) - 1):
                sections[key_list[i]] = content[pos_list[i]:pos_list[i+1]]

            json_sections = json.dumps(sections)
            new_filename = re.sub(r"\.txt$", ".json", filename)
            output_path = os.path.join(output_dir, new_filename)
            with open(output_path, 'w') as f:
                f.write(json_sections)
