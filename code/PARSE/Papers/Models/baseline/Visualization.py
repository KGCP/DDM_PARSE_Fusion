import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

"""
this file is for visualizing the training result
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 8/1/2022 2:18 PM
"""

RECORD_PATH = "../../output/model_Adam_LR0.0001_NL1_ED300_HS300.csv"

df = pd.read_csv(RECORD_PATH, sep='\t', index_col=0)
df['Acc_Train'] = 100 - df['Acc_Train']
df['Acc_Test'] = 100 - df['Acc_Test']
ax = sns.lineplot(data=df)
ax.set_xlabel("Epoch", fontsize = 12)
ax.set_ylabel("Error_rate%", fontsize = 12)
plt.show()