import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import nltk
import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans
from tqdm import tqdm
import os


def train_model():
    global data
    data = pd.read_json("corona2.json")
    print(data.head())
    training_data = [
        {
            "text": example["content"],
            "entities": [
                (annotation["start"], annotation["end"], annotation["tag_name"].upper())
                for annotation in example["annotations"]
            ],
        }
        for example in data["examples"]
    ]
    nlp = spacy.blank("en")
    doc_bin = DocBin()
    for training_example in tqdm(training_data):
        text = training_example["text"]
        labels = training_example["entities"]
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in labels:
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        filtered_ents = filter_spans(ents)
        doc.set_ents(filtered_ents)
        doc_bin.add(doc)
    doc_bin.to_disk("train.spacy")


if __name__ == "__main__":
    # train_model()

    nlp_trained_model = spacy.load("model-best")
