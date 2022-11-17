import json
import utils
import re

# This will remove whitespaces from node types/values, output will be converted with tokenizer and fed to dataset model
# TODO: Add ext info and store as json

with open("output/dps.txt", "r") as fin, open("output/new_ast_raw.json", "w") as fout:
    for line in utils.file_tqdm(fin):
        json_line = json.loads(line)
        nodes = {"nodes": [], "ext": False}
        for node in json_line[0]:
            nodes["nodes"].append(node.strip().replace(" ", "<spc>").encode("unicode_escape").decode())
        nodes["ext"] = json_line[1]
        fout.write(json.dumps(nodes) + "\n")