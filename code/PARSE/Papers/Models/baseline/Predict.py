import re
from PyTorchUtils import *
from PyPDF2 import PdfReader

"""
This file is for predicting the label of txt
author: Bowen Zhang
contact: bowen.zhang1@anu.edu.au
datetime: 7/28/2022 4:24 PM
"""

def extract(label, text):
    i = 0
    res = []
    while i < len(label):
        if label[i] != 'O':
            prefix, name = label[i].split('-')
            start = end = i
            i += 1
            while i < len(label) and label[i] == "I-" + name:
                end = i
                i += 1
            res.append([name, text[start:end + 1]])
        else:
            i += 1
    return res

def get_text_from_pdf():
    path = "../ner_models/dataset/PredictSample/Named_Entity_Extraction_for_Knowledge_Gr.pdf"
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return  text


if __name__ == "__main__":
    # textRaw = get_text_from_pdf()

    with open("../ner_models/dataset/PredictSample/test.txt", "r", encoding="UTF-8") as f:  # 打开文件
        textRaw = f.read()

    text = re.findall(r"[\w']+|[.,!?;]", textRaw)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    _, word2id = getVocab()
    input = torch.tensor([[word2id.get(w, WORD_UNK_ID) for w in text]]).cuda()
    mask = torch.tensor([[1] * len(text)]).bool().cuda()

    model = torch.load(MODEL_DIR + "model_5.pth")
    model.to(device)
    y_pred = model(input, mask)
    id2label, _ = getLabel()
    label = [id2label[l] for l in y_pred[0]]
    result = extract(label, text)
    print(result)