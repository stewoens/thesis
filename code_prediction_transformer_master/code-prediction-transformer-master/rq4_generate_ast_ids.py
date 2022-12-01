import os
import argparse
import json
import logging

from tokenizers import Tokenizer
from utils import file_tqdm

def external(fp, suffix, tokenizer):
    tokenizer = Tokenizer.from_file(tokenizer)
    outfile = "output/{}_ids.txt".format(suffix)
    num_dps = 0
    with open(fp) as fin, open(outfile, "w") as fout:
        for i, line in enumerate(file_tqdm(fin)):
            dp = json.loads(line.strip())
            asts = split(dp, 1000, tokenizer)
            for ast in asts:
                if len(ast) > 1:
                    ids = {"leaf_ids": ast}
                    json.dump(ids, fp=fout)
                    fout.write("\n")
                    num_dps += 1
    logging.info("Wrote {} datapoints to {}".format(num_dps, outfile))

def split(ast, max_len, tokenizer):
    d = []
    leaf_ids = []
    counter = 0

    for i, a in enumerate(ast):
        if "type" in a:
            ids = tokenizer.encode(a["type"]).ids
            d.extend(ids)
            counter += len(ids)
        if "value" in a:
            ids = tokenizer.encode(a["value"]).ids
            d.extend(ids)
            leaf_ids.append(counter)
            counter += len(ids)

    # TODO create list of slices, e.g. [0, 1000] [500, 1500] [1000, 2000], [1500, 2500]...
    # Export ids in respective range, all IDS from leaf_ids that are in range

    # ids from 0 to amount of AST nodes
    ids = list(range(len(d)))

    half_len = int(max_len / 2)

    # AST node count smaller than max_len, simply return
    if len(d) <= max_len:
        return [leaf_ids]

    # First slice from 0 to max_len
    aug_leaf_ids = [ids[:max_len]]
    i = half_len

    result = []

    # Keep filling from i in max_len slices
    while i < len(d) - max_len:
        aug_leaf_ids.append(ids[i : i + max_len])
        i += half_len

    # Add last slice from -max_len to end
    aug_leaf_ids.append(ids[-max_len:])

    # Iterate through all slices
    for a in aug_leaf_ids:
        temp = []
        # Iterate through all leaf IDs
        for l in leaf_ids:
            # Append ID to current slice if in slice a
            if l in a:
                temp.append(l)
        result.append(temp)

    return result

def main():
    parser = argparse.ArgumentParser(description="Parse AST IDs for evaluation")
    parser.add_argument("--ast", help="Filepath with new ASTs")
    parser.add_argument("--out", help="Outfile for ids.txt")
    parser.add_argument("--tokenizer", help="Specify Tokenizer")
    
    args = parser.parse_args()
    if os.path.exists(args.out):
        os.remove(args.out)
    
    tokenizer = Tokenizer.from_file(args.tokenizer)

    num_dps = 0
    with open(args.ast) as fin, open(args.out, "w") as fout, open("output/debug_ids.txt", "w") as fout2:
        for i, line in enumerate(file_tqdm(fin)):
            dp = json.loads(line.strip())
            asts = split(dp, 1000, tokenizer)
            fout2.write("{}: {}\n".format(i, len(asts)))
            for ast in asts:
                if len(ast) > 1:
                    ids = {"leaf_ids": ast}
                    json.dump(ids, fp=fout)
                    fout.write("\n")
                    num_dps += 1
    logging.info("Wrote {} datapoints to {}".format(num_dps, args.out))


if __name__ == "__main__":
    main()