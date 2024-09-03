"""
this file is for splitting training, validation and testing dataset
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 12/9/2022 2:32 pm
"""
import os.path

import pandas as pd

if __name__ == "__main__":
    path = "./dataset/backup/csner_total.csv"
    split_prop = [0.6, 0.8, 1]
    df = pd.read_csv(path)
    length = len(df)
    df_train = df[:int(length*split_prop[0])]
    df_val = df[int(length*split_prop[0]):int(length*split_prop[1])]
    df_test = df[int(length*split_prop[1]):int(length*split_prop[2])]

    output_path = "./dataset/backup/"
    train_out_path = os.path.join(output_path, "train.csv",)
    val_out_path = os.path.join(output_path, "val.csv")
    test_out_path = os.path.join(output_path, "test.csv")

    df_train.to_csv(train_out_path, header=None, index=None)
    df_val.to_csv(val_out_path, header=None, index=None)
    df_test.to_csv(test_out_path, header=None, index=None)

