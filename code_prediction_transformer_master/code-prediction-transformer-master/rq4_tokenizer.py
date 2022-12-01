from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.trainers import WordPieceTrainer
from tokenizers.pre_tokenizers import CharDelimiterSplit

from utils import file_tqdm, separate_dps

import json
import logging
from tqdm import tqdm

# Read all data (py150) and remove comma characters for tokenizer trianing


with open("data/python150k.json") as fin, open("data/python150k_rq4.json", "w") as fout:
    for i, line in enumerate(tqdm(fin)):
        dp = json.loads(line.strip())
        for j, d in enumerate(dp):
            if "value" in d:
                if "," in d["value"]:
                    d["value"].replace(",", " ")
        print(json.dumps(dp), file=fout)

with open("data/python150k_rq4.json") as fin:
    for line in tqdm(fin):
        dp = json.loads(line.strip())
        for d in enumerate(dp):
            if "value" in d:
                if "," in d["value"]:
                    print('Not cleaned up')

# Extract value/types from trees and store in comma separated raw file (all_raw.json)

with open("output/all_new_trees.json") as fin, open("output/all_raw.json", "w") as fout:
    for i, line in enumerate(tqdm(fin)):
        dp = json.loads(line)
        token_list = []
        for d in dp:
            if "value" in d:
                token_list.append(d["value"])
            elif "type" in d:
                token_list.append(d["type"])
        raw = ",".join(token_list)
        print(json.dumps(raw), file=fout)

# Train tokenizer on raw file

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))
tokenizer.pre_tokenizer = CharDelimiterSplit(delimiter=",")
trainer = WordPieceTrainer(special_tokens=["[UNK]", "[PAD]"])

tokenizer.train(["output/all_raw.json"], trainer)

tokenizer.save("output/tokenizer.json")