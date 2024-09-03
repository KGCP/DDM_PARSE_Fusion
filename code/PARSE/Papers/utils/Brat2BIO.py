import os
import shutil
import time

"""
this file is to automaitically convert BRAT to BIO annotation, and copy the converted 
file to dataset folder for further operations
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/26/2022 8:26 PM
"""

# TODO
# need further revision
fileList = ["S0010938X12001163"]

for i in range(len(fileList)):
    script = "python anntoconll.py ../dataset/Training/CandidateDataSet/ScienceIE/" + fileList[i] + ".txt"
    os.system(script)

    # move the condll file to dataset folder for further combination
    fromPath = "../dataset/Training/CandidateDataSet/ScienceIE/" + fileList[i] + ".conll"
    toPath = "../dataset/Training/dataset/"
    shutil.move(fromPath, toPath)


