import pandas as pd

"""
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/28/2022 2:51 PM
"""


if __name__ == "__main__":
    dataset = Dataset('test')
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    loader = data.DataLoader(
        dataset,
        batch_size=100,
        collate_fn=collate_fn
    )


    with torch.no_grad():
        y_true_list = []
        y_pred_list = []
        performance_dict = {}
        RECORD_PATH = RECORD_DIR + f'model_{OPTIMIZER}_LR{LR}_NL{NUM_LAYER}_ED{EMBEDDING_DIM}_HS{HIDDEN_SIZE}.csv'

        n = 100
        for i in range(n):
            # load saved model
            model = torch.load(MODEL_DIR + f'model_{i}_{OPTIMIZER}_LR{LR}_NL{NUM_LAYER}_ED{EMBEDDING_DIM}_HS{HIDDEN_SIZE}.pth')
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
                for y,m in zip(target, mask):
                    # only the real part of sentence will be added to list(del the masked parts)
                    y_true_list += y[m == True].tolist()

            y_true_tensor = torch.tensor(y_true_list)
            y_pred_tensor = torch.tensor(y_pred_list)
            accuracy = (y_true_tensor == y_pred_tensor).sum() / len(y_true_tensor)

            print(">> total:", len(y_true_tensor), 'accuracy:', accuracy.item() * 100)

            performance_dict[i] = accuracy.item() * 100

        df = pd.DataFrame(performance_dict, index=[0]).T
        df.columns = ["Acc_Test"]
        df_origin = pd.read_csv(RECORD_PATH, sep='\t', index_col=0)

        frames = [df, df_origin]
        df_result = pd.concat(frames, axis=1)
        df_result.to_csv(RECORD_PATH, sep='\t')




