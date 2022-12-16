import json

from transformers.tokenization_utils import PreTrainedTokenizer
import utils

from transformers import PreTrainedTokenizerFast

# This will tokenize and add special tokens
# Todo

ast_tok = "<ast>"

tokenizer = PreTrainedTokenizerFast(tokenizer_file = "tokenizer/code-tokenizer.json")

with open("output/new_ast_raw.json", "r") as fin, open("output/converted_train.txt", "w") as fout:
    for line in utils.file_tqdm(fin):
        json_line = json.loads(line)
        json_tokens = json_line["nodes"]
        is_ext = json_line["ext"]
        if not is_ext:
            encoded = tokenizer.encode(ast_tok + " " + " ".join(json_tokens))
        else:
            encoded = tokenizer.encode(" ".join(json_tokens))
        fout.write(" ".join(str(e) for e in encoded) + " \n")