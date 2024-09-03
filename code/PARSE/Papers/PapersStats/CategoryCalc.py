import shutil
from functools import reduce
from typing import Dict
import json
import re
import matplotlib.pyplot as plt
import numpy as np
from ArxivAbbreviationMap import ABBREVIATION_MAP

"""
This script is for calculating the category of papers collection 
   
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/16/2022 3:59 PM
"""

def cleanCategoryDict(categoryDict):
    '''
    drop the irrelevant unknown keys in categoryDict
    @param categoryDict: raw category dictionary, containing irrelevant keys
    @type categoryDict: dict
    @return: cleaned category dictionary
    @rtype: dict
    '''
    for key in list(categoryDict.keys()):
        if key not in ABBREVIATION_MAP.keys():
            del categoryDict[key]
    return categoryDict

def calcCategory(filePath):
    '''

    @param filePath: json file path
    @type filePath: string
    @return: dict categorized by science fields and dict categorized by papers
    @rtype: dict
    '''

    # categoryDict is a nested dict recording main category and subcategory's paper amount
    # like {cs: {ml: 10, cv:20, ....}, phy: {ab: 15, cd: 20...}, ...}
    subCategoryDict: Dict[str, int] = {}
    categoryDict: Dict[str, subCategoryDict] = {}

    # papersDict is a nested dict recording each paper's category and subcategory
    # like {paper1: {cs: {(ml, nlp, ai...)}, phy: {(ab, cd...)}...}, paper2:... }
    papersSubCategory: Dict[str, list] = {}
    papersDict: Dict[str, papersSubCategory] = {}

    totalPapersAmount = 0

    with open(filePath, 'r') as f:
        jsonData = json.load(f)
        for key, value in jsonData.items():
            # if this paper is not downloaded successfully, ignore it
            if not value.get("downloaded"):
                continue
            else:
                totalPapersAmount += 1
            rawCategory = value.get("categories")
            title = value.get('title')
            author = value.get('authors')
            DOI = value.get('doi', "")
            Link = value.get("links", "")
            Time = value.get("published", "")
            if rawCategory == None:
                rawCategory = jsonData[key][key].get("categories")
                title = jsonData[key][key].get('title')
                author = jsonData[key][key].get('authors')
                DOI = jsonData[key][key].get('doi', "")
                Link = jsonData[key][key].get("links", "")
                Time = jsonData[key][key].get("published", "")
            for item in rawCategory:
                if "." in item and not any(chr.isdigit() for chr in item):
                    mainC = re.split(r'\.', item)[0]
                    subC = re.split(r'\.', item)[1]
                    if mainC not in categoryDict.keys():
                        subCategoryDict = {}
                        subCategoryDict[subC] = 1
                        categoryDict[mainC] = subCategoryDict
                    else:
                        subCategoryDict = categoryDict[mainC]
                        if subC not in subCategoryDict.keys():
                            subCategoryDict[subC] = 1
                        else:
                            subCategoryDict[subC] += 1

                    if key not in papersDict.keys():
                        papersSubCategory = {}
                        papersSubCategory[mainC] = []
                        papersSubCategory[mainC].append(subC)
                        papersDict[key] = papersSubCategory
                        papersDict[key]["title"] = title
                        papersDict[key]["author"] = author
                        papersDict[key]["doi"] = DOI
                        papersDict[key]["link"] = Link
                        papersDict[key]["time"] = Time
                    else:
                        if mainC in papersDict[key]:
                            papersDict[key][mainC].append(subC)
                        else:
                            papersDict[key][mainC] = []
                            papersDict[key][mainC].append(subC)
                else:
                    UNKNOWN = "Unknown Subcategory"
                    if item not in categoryDict:
                        categoryDict[item] = {UNKNOWN: 1}
                    else:
                        if UNKNOWN in categoryDict[item].keys():
                            categoryDict[item][UNKNOWN] += 1
                        else:
                            categoryDict[item][UNKNOWN] = 1

                    if key not in papersDict.keys():
                        papersDict[key] = {item: []}
                        papersDict[key][item].append("Unknown_Type")
                        papersDict[key]["title"] = title
                        papersDict[key]["author"] = author
                        papersDict[key]["doi"] = DOI
                        papersDict[key]["link"] = Link
                        papersDict[key]["time"] = Time
                    else:
                        papersDict[key][item] = []
                        papersDict[key][item].append("Unknown_Type")
                        papersDict[key]["title"] = title
                        papersDict[key]["author"] = author
                        papersDict[key]["doi"] = DOI
                        papersDict[key]["link"] = Link
                        papersDict[key]["time"] = Time


    categoryDict = cleanCategoryDict(categoryDict)
    print("total papers amount is: ", totalPapersAmount)

    return categoryDict, papersDict


def analyzeCategoryDict(categoryDict, dumpJson):
    '''
    this function is to analyze the category dict
    @param categoryDict: cleaned categoryDict
    @type categoryDict: dict
    @param dumpJson: if dump the categoryDict to new json file
    @type dumpJson: bool
    @return: none
    @rtype: none
    '''

    eachCategoryAmount = []
    for v0 in categoryDict.values():
        eachCategoryAmount.append(reduce(lambda x, y: x+y, list(v0.values())))
    eachCategoryAmount = np.array(eachCategoryAmount)
    eachCategoryAmountPct = [(x / np.sum(eachCategoryAmount) * 100) for x in eachCategoryAmount]

    categories = list(categoryDict.keys())
    csIndex = categories.index("cs")
    csPapersAmt = eachCategoryAmount[csIndex]

    indList = []
    for index in range(len(eachCategoryAmountPct)):
        if eachCategoryAmountPct[index] < 5:
            indList.append(index)
    eachCategoryAmountPct = list(filter(lambda x: eachCategoryAmountPct.index(x) not in indList, eachCategoryAmountPct))
    categories = list(filter(lambda x: categories.index(x) not in indList, categories))

    eachCategoryAmountPct.append(100 - sum(eachCategoryAmountPct))
    categories.append("others")
    csInd = categories.index("cs")
    eachCategoryAmountPct[0], eachCategoryAmountPct[csInd] = eachCategoryAmountPct[csInd], eachCategoryAmountPct[0]
    categories[0], categories[csInd] = categories[csInd], categories[0]

    y = np.array(eachCategoryAmountPct)

    # Use a custom color map
    colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

    # Create pie chart with custom settings
    wedges, texts, autotexts = plt.pie(y,
                                       labels=categories,
                                       explode=(0.1, 0, 0, 0, 0, 0),
                                       colors=colors,
                                       autopct='%.2f%%',
                                       pctdistance=0.85,
                                       startangle=90)

    # Change the color of the percentage labels to white
    for autotext in autotexts:
        autotext.set_color('white')

    # Create a white circle in the center to make it a donut chart
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    plt.title("Papers Category Distribution Pie-chart")
    plt.text(-1, -1.5, "Computer science papers total amount are %d" % (csPapersAmt))
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

    if dumpJson:
        with open('categories_of_papers.json', 'w') as f:
            json.dump(categoryDict, f)



def analyzePapersDict(papersDict, dumpJson):
    '''
    this function is to analyze the papers dict
    @param papersDict: papersDict
    @type papersDict:dict
    @param dumpJson: if dump dict into json file
    @type dumpJson: bool
    @return: none
    @rtype: none
    '''
    if dumpJson:
        with open('papers_info.json', 'w') as f:
            json.dump(papersDict, f)

        src_path = "papers_info.json"
        dst_path = "../ASKG_Paper_Dataset/paper_info"
        shutil.copy(src_path, dst_path)


if __name__ == '__main__':
    filePath = "arxiv_papers_details_new.json"
    categoryDict, papersDict = calcCategory(filePath)
    analyzeCategoryDict(categoryDict, False)
    analyzePapersDict(papersDict, dumpJson=True)






