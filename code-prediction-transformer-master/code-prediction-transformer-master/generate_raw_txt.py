import json
import utils

# This will escape special characters and remove whitespaces from node types/values, output is base for tokenizer
# TODO: Add ext info and store as json

with open("output/dps.txt", "r") as fin, open("output/new_ast_raw.txt", "w") as fout:
    for line in utils.file_tqdm(fin):
        json_line = json.loads(line)
        nodes = []
        for node in json_line[0]:
            nodes.append(node.strip().replace(" ", "<spc>").encode("unicode_escape").decode())
        fout.write(" ".join(nodes) + "\n")