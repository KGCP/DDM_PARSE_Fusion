"""
This file is to train the NER model
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/27/2022 11:01 PM
"""

import pandas as pd
import torch
from PyTorchUtils import *
from config import *
from NER_Model_V1 import Model
from sklearn.metrics import precision_recall_fscore_support


if __name__ == "__main__":
    dataset = Dataset()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    loader = data.DataLoader(
        dataset,
        batch_size=100,
        shuffle=True,
        collate_fn=collate_fn
    )

    model = Model()
    # move the model to GPU
    model.to(device)

    if (OPTIMIZER == "SGD"):
        optimizer = torch.optim.SGD(model.parameters(), lr=LR)
    elif (OPTIMIZER == "Adadelta"):
        optimizer = torch.optim.Adadelta(model.parameters(), lr=LR)
    else:
        optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    y_true_list = []
    y_pred_list = []
    performance_dict = {}
    RECORD_PATH = RECORD_DIR + f'model_{OPTIMIZER}_LR{LR}_NL{NUM_LAYER}_ED{EMBEDDING_DIM}_HS{HIDDEN_SIZE}.csv'

    for e in range(EPOCH):
        # b is batch
        for b, (input, target, mask) in enumerate(loader):
            # refer to model.forward()
            y_pred = model(input, mask)
            loss = model.loss_fn(input, target, mask)

            # for each epoch, reset the adam optimizer
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if b % 10 == 0:
                print('>> epoch', e, 'loss: ', loss.item())

            for lst in y_pred:
                y_pred_list += lst
            for y,m in zip(target, mask):
                # only the real part of sentence will be added to list(del the masked parts)
                y_true_list += y[m == True].tolist()


        # #  save model after each epoch
        torch.save(model, MODEL_DIR + f'model_{e}_{OPTIMIZER}_LR{LR}_NL{NUM_LAYER}_ED{EMBEDDING_DIM}_HS{HIDDEN_SIZE}.pth')

        # save training result to csv file

        y_true_tensor = torch.tensor(y_true_list)
        y_pred_tensor = torch.tensor(y_pred_list)
        accuracy = (y_true_tensor == y_pred_tensor).sum() / len(y_true_tensor)
        print("Accuracy%:", accuracy.item() * 100)
        performance_dict[e] = accuracy.item() * 100


        performance_df = pd.DataFrame.from_dict(performance_dict, orient="index")
        performance_df.to_csv(RECORD_PATH, sep='\t')


