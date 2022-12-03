import argparse
from utils import file_tqdm
import json
import logging

import generate_new_trees
import rq4_generate_ast_ids

from tokenizers import Tokenizer
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description="Prepare datasets for rq4")
    parser.add_argument("--file_path")
    parser.add_argument("--tokenizer")
    parser.add_argument("--suffix")

    args = parser.parse_args()

    # Generate new trees
    print("Generating new trees")
    generate_new_trees.external(args.file_path, args.suffix)
    # Remove comma character from trees
    print("Removing \",\" character from new trees")
    clean_trees("output/{}_new_trees.json".format(args.suffix), args.suffix)
    # Split trees and traverse DFS, generate DPS
    print("Splitting and encoding trees, generating IDs")
    preprocess("output/{}_new_trees_cleaned.json".format(args.suffix), args.suffix, args.tokenizer)

def split(ast, max_len, tokenizer):
    d = []
    ids = {
        # Is node leaf or internal
        "leaf_ids": [],
        "internal_ids": [],

        # Values 
        "attr_ids": [],
        "num_ids": [],
        "name_ids": [],
        "param_ids": [],
        "string_ids": [],

        # Types
        "call_ids": [],
        "assign_ids": [],
        "return_ids": [],
        "list_ids": [],
        "dict_ids": [],
        "raise_ids": []
    }

    counter = 0

    for i, node in enumerate(ast):

        if "type" in node:
            tokenized_ids = tokenizer.encode(node["type"]).ids
            d.extend(tokenized_ids)
            ids["internal_ids"].append(counter)
            if node["type"] == "attr":
                ids["attr_ids"].append(counter + 1)
            elif node["type"] == "Num":
                ids["num_ids"].append(counter + 1)
            elif node["type"] in {"NameLoad", "NameStore"}:
                ids["name_ids"].append(counter + 1)
            elif node["type"] == "NameParam":
                ids["param_ids"].append(counter + 1)
            elif node["type"] == "Str":
                ids["string_ids"].append(counter + 1)
            elif node["type"] == "Call":
                ids["call_ids"].append(counter)
            elif node["type"] == "Assign":
                ids["assign_ids"].append(counter)
            elif node["type"] == "Return":
                ids["return_ids"].append(counter)
            elif node["type"] in {"ListComp", "ListLoad", "ListStore"}:
                ids["list_ids"].append(counter)
            elif node["type"] in {"DictComp", "DictLoad", "DictStore"}:
                ids["dict_ids"].append(counter)
            elif node["type"] == "Raise":
                ids["raise_ids"].append(counter)    
            counter += len(tokenized_ids)
        elif "value" in node:
            tokenized_ids = tokenizer.encode(node["value"]).ids
            d.extend(tokenized_ids)
            ids["leaf_ids"].append(counter)
            counter += len(tokenized_ids)

    id_range = list(range(len(d)))

    half_len = int(max_len / 2)

    if len(d) <= max_len:
        return [[[d, 0]], [ids]]

    aug_d = [[d[:max_len], 0]]
    aug_leaf_ids = [id_range[:max_len]]

    i = half_len

    while i < len(d) - max_len:
        aug_d.append([d[i : i + max_len], half_len])
        aug_leaf_ids.append(id_range[i : i + max_len])
        i += half_len

    idx = max_len - (len(d) - (i + half_len))
    aug_d.append([d[-max_len:], idx])
    aug_leaf_ids.append(id_range[-max_len:])

    id_result_list = []

    for i, aug_leaf_id_slice in enumerate(aug_leaf_ids):
        diff = min(aug_leaf_id_slice)
        slice_ids = {
            # Is node leaf or internal
            "leaf_ids": [],
            "internal_ids": [],

            # Values 
            "attr_ids": [],
            "num_ids": [],
            "name_ids": [],
            "param_ids": [],
            "string_ids": [],

            # Types
            "call_ids": [],
            "assign_ids": [],
            "return_ids": [],
            "list_ids": [],
            "dict_ids": [],
            "raise_ids": []
        }
        for id_key, id_values in ids.items():
            for id_value in id_values:
                if id_value in aug_leaf_id_slice:
                    slice_ids[id_key].append(id_value - diff)
        id_result_list.append(slice_ids)
    return [aug_d, id_result_list]

def preprocess(fp, suffix, tokenizer):
    tokenizer = Tokenizer.from_file(tokenizer)
    dps_outfile = "output/{}_dps.txt".format(suffix)
    ids_outfile = "output/{}_ids.txt".format(suffix)
    num = 0
    with open(fp) as fin, open(dps_outfile, "w") as fout_dps, open(ids_outfile, "w") as fout_ids:
        for i, line in enumerate(file_tqdm(fin)):
            dp = json.loads(line.strip())
            asts, ids = split(dp, 1000, tokenizer)
            for i, (ast, extended) in enumerate(asts):
                if len(ast) > 1:
                    json.dump([ast, extended], fp=fout_dps)
                    json.dump(ids[i], fp=fout_ids)
                    fout_dps.write("\n")
                    fout_ids.write("\n")
                    num += 1
    logging.info("Wrote {} datapoints to {} and {}".format(num, ids_outfile, dps_outfile))

def clean_trees(fp, suffix):
    with open(fp) as fin, open("output/{}_new_trees_cleaned.json".format(suffix), "w") as fout:
        for i, line in enumerate(tqdm(fin)):
            dp = json.loads(line.strip())
            for j, d in enumerate(dp):
                if "value" in d:
                    if "," in d["value"]:
                        d["value"].replace(",", " ")
            print(json.dumps(dp), file=fout)


if __name__ == "__main__":
    main()