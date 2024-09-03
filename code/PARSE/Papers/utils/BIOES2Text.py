import os
import re

import pandas as pd

"""
This file is to convert BIOES/BIO file back to Raw Text
Some database did not provide the original text, create text by this file
author: PapersStats Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/27/2022 1:30 AM
"""


# for Trainset
inputPath = r"../ASKG_Paper_Dataset/BIO_Format"
outputDir = r"../ASKG_Paper_Dataset/RawTextFromBIO"

for root, dirs, files in os.walk(inputPath):
    for filename in files:
        file_path = os.path.join(inputPath, filename)

        df = pd.read_csv(file_path, sep = '\t')
        df = df.drop(columns=['label'])

        txtList = df['text'].values.tolist()
        txtList = [str(word) for word in txtList]

        output_file = re.sub(r"\.csv$", ".txt", filename)
        outputPath = os.path.join(outputDir, output_file)
        with open(outputPath, "w") as file:
            for i in range(len(txtList) - 1):
                if txtList[i + 1] == "." or txtList[i + 1] == ":":
                    file.write(txtList[i])
                else:
                    file.write(txtList[i] + " ")

