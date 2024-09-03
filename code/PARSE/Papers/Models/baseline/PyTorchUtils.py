import torch
from torch.utils import data
import pandas as pd
from config import *
"""
this is an utils file for pytorch
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/27/2022 3:10 AM
"""

def getVocab():
    df = pd.read_csv(VOCAB_PATH, names=['word', 'id'])
    return list(df['word']), dict(df.values)

def getLabel():
    df = pd.read_csv(LABEL_PATH, names=['label', 'id'])
    return list(df['label']), dict(df.values)

class Dataset(data.Dataset):
    def __init__(self, type='train', base_len=50):
        super().__init__()
        self.base_len = base_len
        sample_path = TRAIN_SAMPLE_DIR if type == 'train' else TEST_SAMPLE_DIR
        self.df = pd.read_csv(sample_path, names=['word', 'label'])
        _, self.word2id = getVocab()
        _, self.label2id = getLabel()
        self.getPoints()

    def __getitem__(self, index):
        '''
        this function is to convert the text to unique number
        each sentence in a batch will be processed, and then pass to collate_fn()
        @param index: index of points, i.e. the splitted text position
        @type index: int
        @return: converted number from character
        @rtype: lists
        '''
        df = self.df[self.points[index] : self.points[index + 1]]
        word_unk_id = self.word2id[WORD_UNK]
        label_o_id =self.label2id['O']

        # if word w is not in wordlist, return word_unk_id
        input = [self.word2id.get(w, word_unk_id) for w in df['word']]
        target = [self.label2id.get(l, label_o_id) for l in df['label']]
        return input, target

    def __len__(self):
        return len(self.points) - 1

    def getPoints(self):
        '''
        count the split point for the whole text. the big text file need to be split, and prevent to split on the I- label
        @param self: None
        @type self: None
        @return: None
        @rtype: None
        '''
        self.points = [0]
        i = 0
        while True:
            if i + self.base_len >= len(self.df):
                self.points.append(len(self.df))
                break
            if self.df.loc[i + self.base_len, 'label'] == 'O':
                i += self.base_len
                self.points.append(i)
            else:
                i += 1

def collate_fn(batch):
    '''
    data verification function for pytorch, like a middleware, this function deal with the data raw input and then
    send the data to NER model
    pytorch dataloader must have same length data input for each batch
    @param batch: sentences of each batch
    @type batch: 2dim list
    @return: input: input word list after padding, target: annotation label list after padding,
    mask: bool value list indicating padding parts
    @rtype: 3 tensor
    '''

    # sort sentences in the batch according to length
    batch.sort(key = lambda x: len(x[0]), reverse = True)
    maxLen = len(batch[0][0])
    input = []
    target = []
    mask = []
    for item in batch:
        padLen = maxLen - len(item[0])
        # fill the input length
        input.append(item[0] + [WORD_PAD_ID] * padLen)
        target.append(item[1] + [LABEL_O_ID] * padLen)
        # mask pad parts with 0. Real sentence words are 1, PAD are 0
        mask.append([1] * len(item[0]) + [0] * padLen)
    # when enumerate(dataloader), this 3 tensor will be returned
    # move the tensor to GPU
    return torch.tensor(input).cuda(), torch.tensor(target).cuda(), torch.tensor(mask).bool().cuda()


if __name__ == '__main__':
    dataset = Dataset()
    # batch_size: define the sentence amount each time, collate_fn: data load middleware for pytorch model
    loader = data.DataLoader(dataset, batch_size=10, collate_fn=collate_fn)


