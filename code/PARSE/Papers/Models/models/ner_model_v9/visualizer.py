"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 20/9/2022 9:23 pm
"""
import json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

def visualize_training_result(result_path):
    result_dict = {}
    with open(result_path, 'r') as f:
        result_dict = json.load(f)

    pretrained_model_name = result_dict['parameters']['pretrained_model']
    mid_struct = result_dict['parameters']['mid_struct']

    df_result = pd.DataFrame()
    train_result_f1 = []
    test_result_f1 = []
    for d_tr in result_dict['train'].values():
        train_result_f1.append(d_tr['f1'])

    for d_te in result_dict['test'].values():
        test_result_f1.append(d_te['f1'])

    total_step = len(train_result_f1)
    df_result['train_result_f1'] = train_result_f1
    df_result['test_result_f1'] = test_result_f1

    p = sns.lineplot(data = df_result)
    p.set_xlabel("step", fontsize=15)
    p.set_ylabel("f1 score", fontsize=15)

    plt.title(f'{pretrained_model_name}-{mid_struct}')
    plt.show()



if __name__ == '__main__':
    result_path = "./result/1663605999.json"
    visualize_training_result(result_path)