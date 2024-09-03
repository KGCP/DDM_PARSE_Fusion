"""
This file is to preprocess the BRAT annotation file

author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/24/2022 6:07 PM
"""

import pandas as pd
from config import *

# def getAnnotation(annotationPath):
#     with open(annotationPath) as f:
#         annotations = {}
#         for line in f.readlines():
#             print(line)
#             arrayTemp = line.split('\t')
#             word = arrayTemp[1].split(' ')
#             name = word[0]
#             wordStart = int(word[1])
#             wordEnd = int(word[-1])
#
#             # in case the annotation is too long
#             if wordEnd - wordStart > 100:
#                 continue
#             annotations[wordStart] = 'B-' + name
#             for i in range(wordStart + 1, wordEnd):
#                 annotations[i] = "I-" + name
#         return annotations

def getText(textPath):
    with open(textPath, encoding='UTF-8') as f:
        return f.read()

# def generateAnnotation():
#     for textPath in glob(ORIGIN_DIR + '*.txt'):
#         annotationPath = textPath[:-3] + 'ann'
#         text = getText("../TrainData/ScienceIE/S0010938X1500195X.txt")
#         # text = getText(textPath)
#         # annotations = getAnnotation(annotationPath)
#         wordList = re.split("\W",text)
#         df = pd.DataFrame({'word': wordList, 'label' : ['o'] * len(wordList)})
#         i = 1

def generateVocab():
    '''
    this function will create a vocabulary list and each vocabulary will have a unique number,
    the list is ordered by the show-up frequency
    @return: None
    @rtype: None
    '''
    df = pd.read_csv(TRAIN_SAMPLE_DIR, usecols=[0], names=['word'])
    vocabList = [WORD_PAD, WORD_UNK] + df['word'].value_counts().keys().tolist()
    # only take the word within word limit 30000 for example, to elimiate the OCR mistakes if any
    vocabList = vocabList[:VOCAB_SIZE]
    vocabDict = {v: k for k, v in enumerate(vocabList)}
    vocab = pd.DataFrame(list(vocabDict.items()))
    vocab.to_csv(VOCAB_PATH, header=None, index=None)

def generateLabel():
    '''
        this function will create a annotation label list and each label will have a unique number,
    the list is ordered by the show-up frequency
    @return:
    @rtype:
    '''
    df = pd.read_csv(TRAIN_SAMPLE_DIR, usecols=[1], names=['label'])
    labelList = df['label'].value_counts().keys().tolist()
    labelDict = {v: k for k, v in enumerate(labelList)}
    label = pd.DataFrame(list(labelDict.items()))
    label.to_csv(LABEL_PATH, header=None, index=None)



if __name__ == '__main__':
    generateVocab()
    generateLabel()



