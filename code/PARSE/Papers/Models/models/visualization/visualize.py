import json
import pandas as pd
import matplotlib.pyplot as plt

with open("1682956992.json", "r") as file:
    json_data = json.load(file)

test_data = json_data["test"]
f1_scores = [item["f1"] for item in test_data.values()]


df = pd.read_csv("model_Adam_LR0.0001_NL1_ED300_HS300.csv", header=None)
baseline_f1_scores = [float(x) for x in df[0].tolist()]

epochs = list(range(len(test_data)))
epochs = [x+1 for x in epochs]
plt.plot(epochs, f1_scores, marker='o', label="CharCNN+SciBERT+BiLSTM+CRF")
plt.plot(epochs, baseline_f1_scores, marker='s', label="BiLSTM+CRF (Baseline)")
plt.xlabel("Epochs")
plt.ylabel("Macro F1 Score")
plt.title("Macro F1 Score Trend Over Epochs")
plt.legend()
plt.grid()
plt.xticks(epochs)
plt.show()
