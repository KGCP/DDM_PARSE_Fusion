"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 1/5/2023 2:16 am
"""
import os

import pandas as pd
from config import *
from PyTorchUtils import *
from config import *
from NER_Model_V1 import Model
from sklearn.metrics import precision_recall_fscore_support


def calculate_metrics(y_true, y_pred, average='macro'):
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average=average)
    return precision, recall, f1


if __name__ == "__main__":
    dataset = Dataset('test')
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    loader = data.DataLoader(
        dataset,
        batch_size=100,
        collate_fn=collate_fn
    )

    y_true_list = []
    y_pred_list = []
    performance_dict = {}
    RECORD_PATH = RECORD_DIR + f'model_{OPTIMIZER}_LR{LR}_NL{NUM_LAYER}_ED{EMBEDDING_DIM}_HS{HIDDEN_SIZE}.csv'

    n = 30
    for i in range(n):
        with torch.no_grad():
            # load saved model
            model = torch.load(
                MODEL_DIR + f'model_{i}_{OPTIMIZER}_LR{LR}_NL{NUM_LAYER}_ED{EMBEDDING_DIM}_HS{HIDDEN_SIZE}.pth')
            # move the model to GPU
            model.to(device)

            for b, (input, target, mask) in enumerate(loader):
                # refer to model.forward()
                y_pred = model(input, mask)

                id2label, _ = getLabel()
                label = [id2label[l] for l in y_pred[0]]

                loss = model.loss_fn(input, target, mask)

                print('>> batch', b, 'loss: ', loss.item())

                for lst in y_pred:
                    y_pred_list += lst
                for y, m in zip(target, mask):
                    # only the real part of sentence will be added to list(del the masked parts)
                    y_true_list += y[m == True].tolist()

            y_true_tensor = torch.tensor(y_true_list)
            y_pred_tensor = torch.tensor(y_pred_list)
            accuracy = (y_true_tensor == y_pred_tensor).sum() / len(y_true_tensor)

            print(">> total:", len(y_true_tensor), 'accuracy:', accuracy.item() * 100)

            precision, recall, f1 = calculate_metrics(y_true_list, y_pred_list)
            performance_dict[i] = {"precision": precision, "recall": recall, "f1": f1,
                                   "accuracy": accuracy.item() * 100}

    filename = os.path.join(RECORD_DIR, 'model_Adam_LR0.0001_NL1_ED300_HS300.csv')

    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)

    performance_df = pd.DataFrame.from_dict(performance_dict, orient="index")

    performance_df.to_csv(filename, sep='\t')
