"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 26/4/2023 3:14 am
"""

import csv

input_file = '../dataset/test_title.csv'
output_file = '../dataset/test_title_v3.csv'

def process_line(line):
    if line == ['.','O']:
        return []
    else:
        return line

with open(input_file, 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    processed_data = [process_line(row) for row in reader]

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(processed_data)

