"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 17/1/2023 5:35 pm
This class is to clean the training and testing dataset.
for example:
"
MUC	O
and	O
SUMMAC	O
play	O
their	O
appropriate	O
roles	O
in	O
the	O
next	O
generation	O
Internet.	O
"
to
"
MUC	O
and	O
SUMMAC	O
play	O
their	O
appropriate	O
roles	O
in	O
the	O
next	O
generation	O
Internet    O
.	O
"
"""
import numpy as np
import pandas as pd

def insert(df, index, df_add):
    df1 = df.iloc[:index, :]
    df2 = df.iloc[index:, :]
    df_new = pd.concat([df1, df_add, df2], ignore_index=True)
    return df_new

if __name__ == '__main__':
    # For testset
    inputPath = r"../Models/models/dataset/train-abs.csv"
    outputPath = r"../Models/models/dataset/train_abs_clean.csv"

    with open(inputPath, 'r', encoding='utf-8') as f:
        text_lines = []
        words = ""
        labels = ""
        df = pd.read_csv(f, names=['words', 'labels'], sep='\t', skip_blank_lines=False)
        cur_length = 0

        insert_pos = []
        for index, row in df.iterrows():
            word = row['words']
            label = row['labels']
            if isinstance(word, str) and len(word) > 1 and word[-1] == "." and index + 1 < len(df) and isinstance(df.loc[index + 1]['words'], str) and df.loc[index + 1]['words'][0].isupper():
                insert_pos.append(index + 1)
                row['words'] = row['words'].strip('.')
            if isinstance(word, str) and len(word) > 1 and word[-1] == "." and index + 1 < len(df) and (df.loc[index + 1]['words'] is np.nan):
                insert_pos.append(index + 1)
                row['words'] = row['words'].strip('.')

        for index, pos in enumerate(insert_pos):
            df_add = pd.DataFrame({'words':['.'], 'labels':['O']})
            df = insert(df, pos + index, df_add)

        df.to_csv(outputPath, index=None, header=None)
