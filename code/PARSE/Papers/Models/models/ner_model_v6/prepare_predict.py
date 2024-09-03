"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 27/9/2022 8:50 pm
"""
import re

if __name__ == '__main__':
    text_path = "./dataset/askg/test.txt"
    with open(text_path, 'r') as f:
        line = f.readline()
        line = re.split("[ ]", line)
        for item in line:
            if "\\n" in item:
                item0 = item.split('\\n')
                i=1

