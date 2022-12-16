import os
import argparse

import generate_new_trees
import generate_vocab
from models.trav_trans import generate_data, generate_ast_ids

def main():
    parser = argparse.ArgumentParser(description="Preprocess py150 train and eval files")
    parser.add_argument("--file_path", help="Specify py150 file path")
    parser.add_argument("--suffix", help="Specify suffix to determine between train/val/test files")
    parser.add_argument("--context_size", default=1000, type=int, help="Specify context size for slicing larger ASTs")
    parser.add_argument("--generate_vocab", default=False, type=bool, help="Specify wether or not to generate a vocab file")
    parser.add_argument("--n_vocab", default=100000, type=int, help="Specify the vocab size")

    args = parser.parse_args()

    # Generate new trees
    generate_new_trees.external(args.file_path, args.suffix)
    # Generate DPS
    generate_data.external("output/{}_new_trees.json".format(args.suffix), args.suffix, args.context_size)
    # Generate Vocab
    if args.generate_vocab:
        generate_vocab.external("output/{}_new_trees.json".format(args.suffix), args.n_vocab)
    # Generate AST IDs
    generate_ast_ids.external("output/{}_new_trees.json".format(args.suffix), args.suffix, args.context_size)

if __name__ == "__main__":
    main()