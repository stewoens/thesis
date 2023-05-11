import json
import ast
import astunparse
from astprint import as_tree, as_code
from cptm.utils import file_tqdm, get_dfs, separate_dps

data = 'OUTPUT/sample_data.json'
out = 'OUTPUT/dps.txt'


def traverse():
    with open(data, "r") as f, open(out, "w") as fout:
        for line in file_tqdm(f):
            # dp = json.loads(line.strip())
            # asts = separate_dps(dp, 1000)
            dp = json.loads(line)
            for cfg in dp:
                #each cfg will generate a different sequence
                for block in cfg:
                    for s in block['statements']:
                        print(s)
                        break

traverse()